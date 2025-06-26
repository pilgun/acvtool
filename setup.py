from setuptools import setup, find_packages

setup(
    name='acvtool',
    version='2.3.4',
    author='Aleksandr Pilgun',
    author_email='alexand.pilgun@gmail.com',
    description="ACVTool is an instrumentation-based tool to measure and visualize instruction coverage for Android apps.",
    url='https://github.com/pilgun/acvtool',
    packages=find_packages(),
    package_data={
        'acvtool': [
            'smiler/libs/jars/*',
            'smiler/resources/logging.yaml',
            'smiler/resources/html/.resources/*',
            'smiler/resources/html/.resources/highlight/*',
            'smiler/resources/html/.resources/highlight/styles/*',
            'smiler/resources/html/templates/*',
            'smiler/resources/instrumentation/smali/tool/acv/*',
    ],},
    install_requires=[
        'PyYAML==6.0.1',
        'Chameleon==4.5.4',
        'javaobj-py3==0.4.4',
        'setuptools<81',
        'lxml==5.4.0',
    ],
    entry_points={
        'console_scripts': [
            'acv=acvtool.acvtool:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.13',
    ],
)