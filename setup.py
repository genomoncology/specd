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
    version='0.8.3',
    author="Ian Maurer",
    author_email='ian@genomoncology.com',

    package_dir={
        '': 'src'
    },

    packages=[
        "specd",
        "specd.sdk",
    ],

    include_package_data=True,

    package_data={
        '': ['*.yaml'],
    },

    install_requires=[
        "click >= 6.7",
        "flask-swagger-ui >= 3.6.0",
        "swagger-spec-validator >= 2.1.0",
        "PyYAML >= 4.2b1",
        "dictdiffer >= 0.7.1",
        "related >= 0.7.3",
        "inflect >= 0.3.1",
        "aiobravado == 0.9.3",
        "bravado == 10.0.0",
        "bravado-core == 5.0.4",
        "bravado-asyncio == 1.0.0",
        "stringcase >= 1.2.0",
        "jsonschema[format]",
        "urllib3 >= 1.24.2",
        "Jinja2 >= 2.10.1",
    ],

    setup_requires=[
        'pytest-runner',
    ],

    license="MIT license",

    keywords="Swagger Open API Specification Bravado",
    description="specd",
    long_description="%s\n\n%s" % (readme, history),
    long_description_content_type="text/markdown",

    entry_points={
        'console_scripts': [
            'specd=specd.cli:cli',
        ],
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
