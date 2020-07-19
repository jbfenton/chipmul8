"""
Setup script.
"""

from setuptools import find_packages, setup


with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()


setup(
    name='chipmul8',
    version='0.1',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    url='https://jbfenton.dev/',
    license='MIT License',
    author='Josh Fenton',
    author_email='josh@jbfenton.dev',
    description='',
    data_files=[("", ["LICENSE"])],
    install_requires=requirements,
    entry_points={
        "console_scripts": ['chipmul8=chipmul8:cli']
    }
)
