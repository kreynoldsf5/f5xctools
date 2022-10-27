# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='f5xctools',
    version='0.1.0',
    description='F5 Distributed Cloud (F5xc) tenant tools.',
    long_description=readme,
    author='Kevin Reynolds',
    author_email='k.reynolds@f5.com',
    url='https://github.com/kreynoldsf5/f5xc-tenant-tools',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'requests>=2.28.1',
        'urllib3>=1.26.12',
        'python-dateutil>=2.8.2'
    ]
)