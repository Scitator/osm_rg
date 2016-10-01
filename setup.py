# setup.py
import os
from distutils.core import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='osm_rg',
    version='1.0',
    author='Kolesnikov Sergey',
    author_email='scitator@gmail.com',
    url='https://github.com/Scitator/osm_rg@wikidata',
    packages=['osm_rg'],
    package_dir={'osm_rg': './osm_rg'},
    package_data={
        'osm_rg': ['wikidata_csv.csv']},
    install_requires=[
        "pandas",
        "numpy==1.11.0",
        "scipy==0.17.1",
    ],
    description='Fast, offline, wikidata based reverse geocoder',
    license='MIT',
    long_description=read('README.md')
)
