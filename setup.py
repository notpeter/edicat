import sys
from setuptools import setup

# This check and everything above must remain compatible with Python 2.7.
if sys.version_info[:2] < (3, 5):
    raise SystemExit("Python >= 3.5 required.")

import edicat  # noqa

# Begin workaround to shave seconds off script execution.
# Issue: https://github.com/pypa/setuptools/issues/510
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
    """Monkey patch for slow stock setuptools get_args implementation."""
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
            args = cls._get_script_args(type_, name, header, script_text)  # noqa
            for res in args:
                yield res


# Monkey patch setuptools ScriptWriter.get_args with our get_args
import setuptools.command.easy_install  # noqa
setuptools.command.easy_install.ScriptWriter.get_args = get_args
# End workaround for pypa/setuptools#510

setup(
    name='edicat',
    version=edicat.__version__,
    description='Print and concatenate EDI files',
    long_description=(
        'Detects EDI X12 and Edifact separators, printing one EDI segment '
        'per line. This allows building shell pipelines (grep, find, etc) '
        'with mixed format EDI files (X12, Edifact, CR, CR/LF, LF, no newlines '
        ' etc.) or just paging through a single EDI file.'
    ),
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
    ],
    keywords='edi edicat edifact ansix12',
    packages=['edicat'],
    python_requires='>=3.5',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'edicat = edicat.__main__:main',
        ],
    },
)
