import os
import sys
from setuptools import setup, find_packages, findall

IRMA_PROBE_PKG_TARGET = os.environ.get('IRMA_PROBE_PKG_TARGET', "Windows")

target = None
target_linux = 0
target_windows = 1
target_str = {target_linux: "linux",
              target_windows: "windows"}

if sys.platform.startswith('win'):
    target = target_windows
else:
    target = target_linux


if IRMA_PROBE_PKG_TARGET == "Linux":
    target = target_linux
elif IRMA_PROBE_PKG_TARGET == "Windows":
    target = target_windows

print "Packaging/Installing for Target '{0}'".format(target_str[target])

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
    scripts=scripts,
)
