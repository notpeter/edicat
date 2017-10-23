from setuptools import setup, find_packages
from codecs import open
from os import path

import edicat

### Workaround for https://github.com/pypa/setuptools/issues/510
import setuptools.command.easy_install
TEMPLATE = '''\
# -*- coding: utf-8 -*-
# EASY-INSTALL-ENTRY-SCRIPT: '{3}','{4}','{5}'
__requires__ = '{3}'
import re
import sys

from {0} import {1}

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit({2}())
'''

@classmethod
def get_args(cls, dist, header=None):
    if header is None:
        header = cls.get_header()
    spec = str(dist.as_requirement())
    for type_ in 'console', 'gui':
        group = type_ + '_scripts'
        for name, ep in dist.get_entry_map(group).items():
            # ensure_safe_name
            if '/' in name:
                raise ValueError("Path separators not allowed in script names")
            script_text = TEMPLATE.format(ep.module_name, ep.attrs[0],
                                          '.'.join(ep.attrs), spec, group, name)
            args = cls._get_script_args(type_, name, header, script_text)
            for res in args:
                yield res


setuptools.command.easy_install.ScriptWriter.get_args = get_args
### End Workaround

setup(
    name='edicat',
    version=edicat.__version__,
    description='Print and concatenate EDI files',
    long_description=open(path.join(path.abspath(path.dirname(__file__)),
                                    'README.md'), encoding='utf-8').read(),
    url='https://github.com/notpeter/edicat',
    author='Peter Tripp',
    author_email='peter.tripp@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='edi edicat edifact ansix12',
    packages=['edicat'],
    python_requires='>=3.5',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'edicat = edicat.__main__:main',
            'ec = edicat.__main__:main',
        ],
    },
)
