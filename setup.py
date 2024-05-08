from setuptools import setup, find_packages

setup(
    name='acvtool',
    version='2.2',
    author='Aleksandr Pilgun',
    author_email='alexand.pilgun@gmail.com',
    description="ACVTool is an instrumentation-based tool to measure and visualize instruction coverage for Android apps.",
    url='https://github.com/pilgun/acvtool',
    packages=find_packages(),
    install_requires=[
        'PyYAML==6.0',
        'Chameleon==4.5.4',
        'lxml==4.9.2',
        'javaobj-py3==0.4.4',
        'six==1.12.0',
        'androguard==4.0.2',
        'pyaxml==0.0.5',
        'typing_extensions==4.7.1'
    ],
    entry_points={
        'console_scripts': [
            'acv=acvtool:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)