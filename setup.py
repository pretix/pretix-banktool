import os

from setuptools import setup, find_packages

try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''

setup(
    name='pretix-banktool',
    version='0.2.0',
    description='Command-line client for pretix that allows to synchronize bank transaction statements to pretix',
    long_description=long_description,
    url='https://github.com/pretix/pretix-banktool',
    author='Raphael Michel',
    author_email='mail@raphaelmichel.de',

    install_requires=[
        'click==6.*',
        'fints==0.2.*',
        'requests',
    ],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,

    entry_points={
        'console_scripts': ['pretix-banktool=pretix_banktool.main:main'],
    },
)
