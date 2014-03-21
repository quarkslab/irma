from setuptools import setup, find_packages

setup(
    name='irma-brain',
    version='1.0',
    author='QuarksLab',
    author_email='irma@quarkslab.com',
    packages=find_packages(),
    include_package_data=True,
    license='LICENSE',
    description='Brain package for IRMA',
    long_description=open('README.rst').read(),
    scripts=['scripts/status.py'],
)
