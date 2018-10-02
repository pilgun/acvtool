from distutils.core import setup

from setuptools import find_packages

setup(
    name='acvtool',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'javaobj==0.1.0',
        'chameleon==3.1',
        'pyyaml==3.12',
        'lxml==4.1.1',
        'six==1.11.0'],
    entry_points={
        'console_scripts': [
            'acv=acvtool:main',
        ]
    }
)
