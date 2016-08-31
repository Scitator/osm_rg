# setup.py
import os
from distutils.core import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='osm_rg',
    version='1.0',
    author='Kolesnikov Sergey',
    author_email='sergey.s.kolesnikov@phystech.edu',
    url='https://github.com/Scitator/osm_rg',
    packages=['osm_rg'],
    package_dir={'osm_rg': './osm_rg'},
    package_data={
        'osm_rg': ['rg_cities15000.csv', 'osm_columns.txt', 'osm_data.txt']},
    setup_requires=[
        'numpy',
        'scipy',
        'geopy',
        'pandas'
    ],
    install_requires=[
        'numpy',
        'scipy',
        'gxeopy',
        'pandas'
    ],
    description='Fast, offline, osm based reverse geocoder',
    license='MIT',
    long_description=read('README.md')
)
