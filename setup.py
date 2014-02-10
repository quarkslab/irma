from setuptools import setup, find_packages

setup(
    name='irma-brain',
    version='0.1',
    author='QuarksLab',
    author_email='irma@quarkslab.com',
    packages=find_packages(),
    license='LICENSE',
    description='Brain package for IRMA',
    long_description=open('README.rst').read(),
    install_requires = ['celery>=3.1.5','redis>=2.8.0','pymongo>=2.6.3'],
)
