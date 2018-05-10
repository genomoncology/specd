#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

history = ""

with open('dev-requirements.txt') as dev_requirements_file:
    tests_require = [r.strip() for r in dev_requirements_file.readlines()]

setup(
    name="specd",
    version='0.1.3',

    package_dir={
        '': 'src'
    },

    packages=[
        "specd",
    ],

    include_package_data=True,

    package_data={
    },

    install_requires=[
        "click >= 6.7",
        "flask-swagger-ui >= 3.6.0",
        "swagger-spec-validator >= 2.1.0",
        "PyYAML >= 3.12",
        "dictdiffer >= 0.7.1",
        "related >= 0.6.3",
        "inflect >= 0.3.1",
    ],

    setup_requires=[
        'pytest-runner',
    ],

    license="MIT license",

    keywords='',
    description="specd",
    long_description="%s\n\n%s" % (readme, history),

    entry_points={
        'console_scripts': [
            'specd=specd.cli:cli',
        ],
    },

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Framework :: Pytest',
    ],
)
