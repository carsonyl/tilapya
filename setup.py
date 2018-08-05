#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for Tilapya."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests>=2.18.4,<3.0.0',
    'marshmallow>=3.0.0b13,<4.0.0',
    'pytz',
]

setup_requirements = [
]

test_requirements = [
    'pytest-runner',
    'pytest>=3.4.0',
    'pytest-vcr>=0.3.0',
]

setup(
    name='tilapya',
    version='0.1.0',
    description='TransLink Open API, in Python.',
    long_description=readme + '\n\n' + history,
    author='Carson Lam',
    author_email='carson.lam@alumni.ubc.ca',
    url='https://github.com/carsonyl/tilapya',
    packages=find_packages(include=['tilapya']),
    include_package_data=True,
    install_requires=requirements,
    license='Apache Software License 2.0',
    zip_safe=False,
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    keywords='tilapya vancouver transit translink',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
