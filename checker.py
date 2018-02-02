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
            yield {
                'type': 'issue',
                'check_name': 'Incorrectly Sorted Imports',
                'description': 'Imports are incorrectly sorted',
                'categories': ['Style'],
                'location': {
                    'path': os.path.relpath(path, start='/code'),
                    'lines': {
                        'begin': 1,
                        'end': 1}},
                'remediation_points': 50000,
                'severity': 'minor'}


def analyze(path):
    if is_python_file(path):
        yield from analyze_file(path)


if __name__ == '__main__':
    with open('/config.json') as config_file:
        config = json.load(config_file)
    for path in config['include_paths']:
        results = analyze(os.path.join('/code', path))
        for problem in results:
            print(json.dumps(problem), end='\0', flush=True)
