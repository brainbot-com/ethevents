#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('requirements.txt') as requirements:
    reqs = requirements.read().split('\n')
with open('requirements-dev.txt') as requirements_dev:
    reqs += requirements_dev.read().split('\n')[1:]

reqs = [req for req in reqs if req and req[0] != '#']

config = {
    'packages': find_packages(),
    'scripts': [],
    'name': 'ethevents',
    'entry_points': {
        'console_scripts': [
            'ethevents=ethevents.ui:entrypoint',
            'ethevents-proxy=ethevents.client.proxy:entrypoint'
        ]
    },
    'install_requires': reqs
}
setup(**config)
