import os
from setuptools import setup, find_packages, findall

IRMA_PROBE_PKG_TARGET = os.environ.get('IRMA_PROBE_PKG_TARGET', "Windows")

target = None
target_linux = 0
target_windows = 1

if IRMA_PROBE_PKG_TARGET == "Linux":
    target = target_linux
elif IRMA_PROBE_PKG_TARGET == "Windows":
    target = target_windows

if target is None:
    raise ValueError("invalid env variable IRMA_PROBE_PKG_TARGET")
else:
    print "Packaging for Target '{0}'".format(IRMA_PROBE_PKG_TARGET)

basename = 'irma-probe'
if target == target_linux:
    name = basename + "-linux"
    scripts = []
elif target == target_windows:
    name = basename + "-win"
    scripts = ['scripts/celery.bat']

setup(
    name=name,
    version='1.0',
    author='QuarksLab',
    author_email='irma@quarkslab.com',
    packages=find_packages(),
    include_package_data=True,
    license='LICENSE',
    description='Probe package for IRMA',
    long_description='',
    install_requires=['celery>=3.1.5', 'redis>=2.8.0'],
)
