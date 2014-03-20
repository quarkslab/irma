from setuptools import setup, find_packages

setup(
    name="irma-probe",
    version='1.0',
    author='QuarksLab',
    author_email='irma@quarkslab.com',
    packages=find_packages(),
    include_package_data=True,
    license='LICENSE',
    description='Probe package for IRMA',
    long_description=open('README.rst').read(),
    scripts=['scripts/celery.bat'],
    install_requires=['celery>=3.1.5', 'redis>=2.8.0'],
)