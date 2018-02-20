import json
import os
import re
import sys
from contextlib import contextmanager
from io import StringIO

from isort import SortImports

shebang_re = re.compile(br'^#!.*\bpython[23w]?\b')


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
        with open(path, 'rb') as fp:
            line = fp.readline(100)
    except IOError:
        return False
    else:
        return bool(shebang_re.match(line))


def analyze_file(path):
    try:
        with suppress_stdout():
            result = SortImports(path, check=True)
    except Exception:
        pass
    else:
        if result.incorrectly_sorted:
            line_no = (
                result.import_index + 1 if result.import_index >= 0 else 1)
            yield {
                'type': 'issue',
                'check_name': 'Incorrectly Sorted Imports',
                'description': 'Imports are incorrectly sorted',
                'categories': ['Style'],
                'location': {
                    'path': os.path.relpath(path, start='/code'),
                    'lines': {
                        'begin': line_no,
                        'end': line_no}},
                'remediation_points': 50000,
                'severity': 'minor'}


def get_files_in_path(path):
    if os.path.isdir(path):
        for dirpath, _dirnames, filenames in os.walk(path, topdown=True):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if is_python_file(filepath):
                    yield filepath
    else:
        yield path


def analyze(path):
    for file_name in get_files_in_path(path):
        if is_python_file(file_name):
            yield from analyze_file(file_name)


if __name__ == '__main__':
    with open('/config.json') as config_file:
        config = json.load(config_file)
    for path in config['include_paths']:
        results = analyze(os.path.join('/code', path))
        for problem in results:
            print(json.dumps(problem), end='\0', flush=True)
