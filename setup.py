from setuptools import setup, find_packages

setup(
    name='irma-frontend',
    version='1.0',
    author='QuarksLab',
    author_email='irma@quarkslab.com',
    packages=find_packages(),
    license='LICENSE',
    description='Brain package for IRMA',
    long_description=open('README.rst').read(),
    install_requires = ['celery>=3.1.5','redis>=2.8.0','pymongo>=2.6.3','bottle>=0.11.6'],
)
