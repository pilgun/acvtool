from setuptools import setup, find_packages

setup(
    name='acvtool',
    version='2.0',
    author="Aleksandr Pilgun",
    description="ACVTool is an instrumentation-based tool to measure and visualize instruction coverage for Android apps.",
    packages=find_packages(),
    install_requires=[
        'PyYAML==5.4.1',
        'Chameleon==3.9.0',
        'lxml==4.6.2',
        'javaobj==0.1.0',
        'six==1.12.0'
        ],
    entry_points={
        'console_scripts': [
            'acv=acvtool:main',
        ]
    }
)
