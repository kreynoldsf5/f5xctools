# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='f5xc-tenant-tools',
    version='0.1.0',
    description='F5 Distributed Cloud (F5xc) tenant tools.',
    long_description=readme,
    author='Kevin Reynolds',
    author_email='k.reynolds@f5.com',
    url='https://github.com/kreynoldsf5/f5xc-tenant-tools',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)