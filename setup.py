#!/usr/bin/env python

# Copied from https://github.com/warner/python-ecdsa

import os
import subprocess
import shutil
import re
from distutils.core import setup, Command
from distutils.command.sdist import sdist as _sdist
from distutils.archive_util import make_zipfile


ANSIBLE_VAR_FILE = "ansible/playbooks/group_vars/all.yml"
VERSION_FILE = "common/src/__init__.py"
VERSION_PY = """#
# Copyright (c) 2013-2018 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

__version__ = '%s'
"""


def update_version_py():
    if not os.path.isdir(".git"):
        print("This does not appear to be a Git repository.")
        return
    try:
        p = subprocess.Popen(["git", "describe",
                              "--tags", "--dirty", "--always"],
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
    except EnvironmentError:
        print("unable to run git, leaving version alone")
        return
    stdout = p.communicate()[0]
    if p.returncode != 0:
        print("unable to run git, leaving version alone")
        return
    ver = stdout.strip()
    write_version_file(ver)


def write_version_file(ver):
    with open(VERSION_FILE, "w") as f:
        f.write(VERSION_PY % ver)
    print("set version to '{}'".format(ver))


def update_ansible_version(version):
    with open(ANSIBLE_VAR_FILE, "r") as f:
        ansible_vars = f.read()
    with open(ANSIBLE_VAR_FILE, "w") as f:
        f.write(ansible_vars.replace("irma_release: HEAD",
                                     "irma_release: {}".format(version)))
    print("version set in default ansible vars")


def get_version():
    try:
        f = open(VERSION_FILE)
    except EnvironmentError:
        return None
    for line in f.readlines():
        mo = re.match("__version__ = '([^']+)'", line)
        if mo:
            ver = mo.group(1)
            return ver
    return None


class Version(Command):
    description = "update version from Git repo"
    user_options = []
    boolean_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        update_version_py()
        print("Version is now: '{}'".format(get_version()))


class Package(_sdist):

    @staticmethod
    def _create_manifest_git():
        cmd = "git ls-tree --name-only -r HEAD"
        file_list = subprocess.check_output(cmd, shell=True, )
        with open('MANIFEST.in', 'w') as manifest:
            for filename in file_list.decode('utf-8').splitlines():
                manifest.write('include {}\n'.format(filename))

    @staticmethod
    def _append_manifest(filelist):
        with open('MANIFEST.in', 'a') as manifest:
            for filename in filelist:
                manifest.write('include {}\n'.format(filename))

    def run(self):
        update_version_py()
        # unless we update this, the sdist command will keep using the old
        version = get_version()
        update_ansible_version(version)
        dest_dir = "ansible/playbooks/files"
        extra_files = ["ansible/irma-ansible/irma-ansible.py"]

        webui_archive = "core-webui-{}".format(version)
        webui_archive_path = os.path.join(dest_dir, webui_archive)
        print("Packaging {}.zip".format(webui_archive))
        # webui dist is generated in
        # root_folder/frontend/web/dist
        if os.path.exists("frontend/web/dist"):
            extra_files.append(webui_archive_path + ".zip")
            shutil.make_archive(webui_archive_path, "zip",
                                base_dir="frontend/web/dist")
            cmd = "git clean -fd frontend/web"
            del_list = subprocess.check_output(cmd, shell=True, )

        for subproj in ["common", "frontend", "brain", "probe"]:
            subproj_archive = "{}-{}".format(subproj, version)
            subproj_archive_path = os.path.join(dest_dir, subproj_archive)
            print("Packaging {}.zip".format(subproj_archive))
            extra_files.append(subproj_archive_path + ".zip")
            shutil.make_archive(subproj_archive_path, "zip", root_dir=subproj)

        self._create_manifest_git()
        self._append_manifest(extra_files)
        self.distribution.metadata.version = version
        _sdist.run(self)
        return


setup(name="core",
      version=get_version(),
      description="IRMA Core",
      author="Quarkslab",
      author_email="irma-info@quarkslab.com",
      url="http://irma.quarkslab.com/",
      license="Apache2",
      cmdclass={"version": Version, "package": Package},
      package_data=True,
      )
