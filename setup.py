#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from timerun import __version__


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='timerun',
    version=__version__,
    author='HH-MWB',
    author_email='h.hong@mail.com',
    description='Library for execution time measurement',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/HH-MWB/timerun',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    py_modules=['timerun'],
    python_requires='>=3.4',
)
