from setuptools import setup, find_packages
from codecs import open
from os import path

import edicat

here = path.abspath(path.dirname(__file__))

# Include contents of README.md as the long_description
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='edicat',
    version=edicat.__version__,
    description='Print and concatenate EDI files',
    long_description=long_description,
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
            'edicat = edicat.cli:main',
            'ec = edicat.cli:main',
        ],
    },
)
