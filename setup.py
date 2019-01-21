import sys
import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('py_scheduler/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

if sys.version_info < (3, 2):
    raise NotImplementedError("Sorry, you need at least Python 3.x")

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='py_scheduler',
    version=version,
    packages=['py_scheduler'],
    url='',
    license='',
    author='py_scheduler',
    author_email='',
    description=''
)