#!/usr/bin/env python3
from setuptools import setup

setup(
    name='liquidtime',
    version='0.1',
    packages=['liquidtime'],
    install_requires=[
        'requests',
        'click',
        'pyyaml'
    ],
    entry_points='''
        [console_scripts]
        liquidtime=liquidtime:cli
    ''',
)
