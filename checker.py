import json
import os
import re
import sys
from contextlib import contextmanager
from difflib import unified_diff
from io import StringIO

from isort import SortImports

SHEBANG_RE = re.compile(br'^#!.*\bpython[23w]?\b')


@contextmanager
def suppress_stdout():
    before = sys.stdout
    sys.stdout = StringIO()
    try:
        yield
    finally:
        sys.stdout = before


def is_python_file(path):
    if path.endswith('.py'):
        return True
    try:
        with open(path, 'rb') as suspect:
            line = suspect.readline(100)
    except IOError:
        return False
    else:
        return bool(SHEBANG_RE.match(line))


def analyze_file(path):
    try:
        with suppress_stdout():
            result = SortImports(path, check=True)
    except Exception:
        pass
    else:
        if result.incorrectly_sorted:
            file_path = os.path.relpath(path, start='/code')
            line_no = (
                result.import_index + 1 if result.import_index >= 0 else 1)
            file_contents = '\n'.join(result.in_lines)
            diff = unified_diff(
                file_contents.splitlines(True),
                result.output.splitlines(True),
                fromfile=file_path,
                tofile=file_path)
            content = {
                'body':
                    'Suggested change:\n\n```diff\n%s\n```' % (
                        ''.join(diff), )}
            yield {
                'type': 'issue',
                'check_name': 'Incorrectly Sorted Imports',
                'description': 'Imports are incorrectly sorted',
                'content': content,
                'categories': ['Style'],
                'location': {
                    'path': file_path,
                    'lines': {
                        'begin': line_no,
                        'end': line_no}},
                'remediation_points': 50000,
                'severity': 'minor'}


def get_files_in_path(path):
    if os.path.isdir(path):
        for dirpath, _dirnames, filenames in os.walk(path, topdown=True):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if is_python_file(file_path):
                    yield file_path
    else:
        yield path


def analyze(path):
    for file_name in get_files_in_path(path):
        if is_python_file(file_name):
            yield from analyze_file(file_name)


def check():
    with open('/config.json') as config_file:
        config = json.load(config_file)
    for path in config['include_paths']:
        results = analyze(os.path.join('/code', path))
        for problem in results:
            print(json.dumps(problem), end='\0', flush=True)


if __name__ == '__main__':
    check()
