#!/usr/bin/env python3
from setuptools import setup

setup(
    name='liquidtime',
    version='0.1',
    py_modules=['liquidtime'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        liquidtime=liquidtime:helpme
    ''',
)
