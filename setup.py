#
# Copyright (c) 2013-2014 QuarksLab.
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

import os
import sys
import fnmatch
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from collections import OrderedDict
from os.path import join, normpath, exists, dirname, abspath
from setuptools import setup, find_packages, Command
from distutils.command.sdist import sdist as _sdist
from distutils.errors import DistutilsOptionError


# =========
#  Helpers
# =========

def include_data(directory, pattern="*", recursive=True, base=""):
    data = []
    if recursive:
        walk_iter = os.walk(directory, followlinks=True)
    else:
        walk_iter = [(directory, [], os.listdir(directory))]
    for (root, dirs, files) in walk_iter:
        filelist = []
        for filename in fnmatch.filter(files, pattern):
            filelist.append(join(root, filename))
        if filelist:
            data.append((normpath(join(base, root)), filelist))
    return data


# Configuration generators
# NOTE: will be moved to module folders in the next releases
def save_config(filename, config, header=None):
    # save the configuration file to the specified file.
    parser = ConfigParser.ConfigParser(dict_type=OrderedDict)
    for section, options in config.iteritems():
        for option, value in options.iteritems():
            if not parser.has_section(section):
                parser.add_section(section)
            parser.set(section, option, str(value))
    filedesc = open(filename, "w")
    if header is not None:
        for line in header.split("\n"):
            filedesc.write("; {line}\n".format(line=line))
    parser.write(filedesc)
    filedesc.close()


def ask(question, answer_type=str, default=None):
    # adjust everything for python2 and python 3
    # TODO: should be moved in a compat module instead
    if sys.version_info[0] == 2:
        input = raw_input

    if answer_type is str:
        answer = ''
        while True:
            if default:
                answer = input('> {0} [{1}] '.format(question, default))
            else:
                answer = input('> {0} '.format(question, default))
            answer = answer.strip()
            if len(answer) <= 0:
                if default:
                    answer = default
                    break
                else:
                    print('You must enter something')
            else:
                break
        return answer
    elif answer_type is bool:
        answer = None
        while True:
            if default is True:
                answer = input('> {0} (Y/n) '.format(question))
            elif default is False:
                answer = input('> {0} (y/N) '.format(question))
            else:
                answer = input('> {0} (y/n) '.format(question))
            answer = answer.strip().lower()
            if answer in ('y', 'yes'):
                answer = True
                break
            elif answer in ('n', 'no'):
                answer = False
                break
            elif not answer:
                answer = default
                break
            else:
                print("You must answer 'yes' or 'no'")
        return answer
    elif answer_type is int:
        answer = None
        while True:
            if default is not None:
                answer = input('> {0} [{1}] '.format(question, default))
            else:
                answer = input('> {0} '.format(question))
            answer = answer.strip()
            if not answer:
                answer = default
            try:
                answer = int(answer)
                break
            except:
                print('You must enter an integer')
        return answer
    else:
        raise NotImplemented()


# =================
#  Custom commands
# =================


class sdist(_sdist):

    def run(self):
        # call build sphinx to build docs
        self.run_command("build_sphinx")
        # call parent install data
        _sdist.run(self)


class configure(Command):

    description = "Configure IRMA's probe application and modules"

    # NOTE: user defined option must be defined with the following format:
    # tuple ('long option', 'short option', 'description')
    user_options = [
        # Add option to configure the probe application
        (
            'application',
            None,
            'Configure IRMA probe application.'
        ),
        # Add option to configure the NSRL module
        (
            'NSRL',
            None,
            'Configure the National Software Reference Library (NSRL) module.'
        ),
        # Add option to configure the VirusTotal module
        (
            'VirusTotal',
            None,
            'Configure the VirusTotal module.'
        ),
        # Add install base option
        (
            'install-base=',
            None,
            "base installation directory."
        ),
    ]

    boolean_options = ['application', 'NSRL', 'VirusTotal']

    def initialize_options(self):
        # install_base is set to None so we can detect if its value is set
        self.install_base = dirname(abspath(sys.argv[0]))
        # by default, we do not force the configuration of modules.
        # NOTE: one can enable the configuration of a module with a command
        # such as the following: python setup.py configure --NSRL --VirusTotal
        self.application = False
        self.NSRL = False
        self.VirusTotal = False

    def finalize_options(self):
        # check for install_base installation directory
        if self.install_base is not None:
            self.install_base = self.install_base.strip()
        if self.install_base == '':
            raise DistutilsOptionError("install-base option not supplied")
        # as setuptools returns integers, simply cast to boolean
        self.application = bool(self.application)
        self.NSRL = bool(self.NSRL)
        self.VirusTotal = bool(self.VirusTotal)

    def run(self):
        configure_list = [
            (self.application, self._configure_application),
            (self.NSRL, self._configure_nsrl),
            (self.VirusTotal, self._configure_virustotal)
        ]
        for (enabled, handle) in configure_list:
            if enabled:
                try:
                    handle()
                except EOFError:
                    pass

    def _configure_application(self):
        # define default configuration
        configuration = OrderedDict()
        configuration['log'] = OrderedDict()
        configuration['log']['syslog'] = False
        configuration['probe'] = OrderedDict()
        configuration['probe']['name'] = 'irma-probe'
        configuration['broker_probe'] = OrderedDict()
        configuration['broker_probe']['host'] = 'brain.irma'
        configuration['broker_probe']['vhost'] = None
        configuration['broker_probe']['username'] = None
        configuration['broker_probe']['password'] = None
        configuration['backend_probe'] = OrderedDict()
        configuration['backend_probe']['host'] = 'brain.irma'
        configuration['backend_probe']['db'] = 1
        configuration['ftp_brain'] = OrderedDict()
        configuration['ftp_brain']['host'] = 'brain.irma'
        configuration['ftp_brain']['username'] = None
        configuration['ftp_brain']['password'] = None

        # show a simple banner
        print("""

Welcome to IRMA probe application configuration script.

The following script will help you to create a new configuration for
IRMA probe application.

Please answer to the following questions so this script can generate the files
needed by the application. To abort the configuration, press CTRL+D.

        """)

        # check for path
        config_file = 'config/probe.ini'
        if not exists(normpath(join(self.install_base, config_file))):
            raise DistutilsOptionError(
                "Cannot find {0} file. Adjust --install-base "
                "option to IRMA installation directory.".format(config_file)
            )

        # log configuration
        configuration['log']['syslog'] = \
            int(ask('Do you want to enable syslog logging? (experimental)',
                    answer_type=bool, default=configuration['log']['syslog']))
        # probe configration
        configuration['probe']['name'] = \
            ask('Which name would you like to give to your probe?',
                answer_type=str, default=configuration['probe']['name'])
        # broker_probe configuration
        configuration['broker_probe']['host'] = \
            ask('What is the hostname of your RabbitMQ server?',
                answer_type=str, default=configuration['broker_probe']['host'])
        configuration['broker_probe']['vhost'] = \
            ask('What is the vhost defined for probes on your '
                'RabbitMQ server?',
                answer_type=str)
        configuration['broker_probe']['username'] = \
            ask('What is the username for this vhost on your RabbitMQ server?',
                answer_type=str)
        configuration['broker_probe']['password'] = \
            ask('What is the password for this vhost on your RabbitMQ server?',
                answer_type=str)
        # backend_probe configuration
        configuration['backend_probe']['host'] = \
            ask('What is the hostname of your Redis server?',
                answer_type=str,
                default=configuration['backend_probe']['host'])
        configuration['backend_probe']['db'] = \
            ask('Which database id is used for probes on your Redis server?',
                answer_type=int, default=configuration['backend_probe']['db'])
        # ftp brain configuration
        configuration['ftp_brain']['host'] = \
            ask('What is the hostname of your FTPs server?',
                answer_type=str, default=configuration['ftp_brain']['host'])
        configuration['ftp_brain']['username'] = \
            ask('What is the username defined for probes on your FTP server?',
                answer_type=str,
                default=configuration['ftp_brain']['username'])
        configuration['ftp_brain']['password'] = \
            ask('What is the password defined for probes on your FTP server?',
                answer_type=str,
                default=configuration['ftp_brain']['password'])

        # write configuration
        config_file = normpath(join(self.install_base, config_file))
        save_config(config_file, configuration)

    def _configure_virustotal(self):
        # define default configuration
        configuration = OrderedDict()
        configuration['VirusTotal'] = OrderedDict()
        configuration['VirusTotal']['private'] = False
        configuration['VirusTotal']['apikey'] = None

        # show a simple banner
        print("""

Welcome to IRMA VirusTotal module configuration script.

The following script will help you to create a new configuration for
VirusTotal module on IRMA probe application.

Please answer to the following questions so this script can generate the files
needed by the application. To abort the configuration, press CTRL+D.

        """)

        # check for path
        config_file = 'modules/external/virustotal/config.ini'
        if not exists(normpath(join(self.install_base, config_file))):
            raise DistutilsOptionError(
                "Cannot find {0} file. Adjust --install-base "
                "option to IRMA installation directory.".format(config_file)
            )

        # VirusTotal configuration
        configuration['VirusTotal']['private'] = \
            ask('Do you want to use VirusTotal private API?',
                answer_type=bool,
                default=configuration['VirusTotal']['private'])
        configuration['VirusTotal']['apikey'] = \
            ask('What is the apikey you would you like to use for VirusTotal?',
                answer_type=str)

        # write configuration
        config_file = normpath(join(self.install_base, config_file))
        save_config(config_file, configuration)

    def _configure_nsrl(self):
        # define default configuration
        configuration = OrderedDict()
        configuration['NSRL'] = OrderedDict()
        configuration['NSRL']['nsrl_os_db'] = None
        configuration['NSRL']['nsrl_mfg_db'] = None
        configuration['NSRL']['nsrl_file_db'] = None
        configuration['NSRL']['nsrl_prod_db'] = None

        # show a simple banner
        print("""

Welcome to IRMA NSRL module configuration script.

The following script will help you to create a new configuration for
NSRL module on IRMA probe application.

Please answer to the following questions so this script can generate the files
needed by the application. To abort the configuration, press CTRL+D.

        """)

        # check for paths
        config_file = 'modules/database/nsrl/config.ini'
        if not exists(normpath(join(self.install_base, config_file))):
            raise DistutilsOptionError(
                "Cannot find {0} file. Adjust --install-base "
                "option to IRMA installation directory.".format(config_file)
            )

        # VirusTotal configuration
        configuration['NSRL']['nsrl_os_db'] = \
            ask('Where is located NSRL OS database?',
                answer_type=str)
        configuration['NSRL']['nsrl_mfg_db'] = \
            ask('Where is located NSRL MFG database?',
                answer_type=str)
        configuration['NSRL']['nsrl_prod_db'] = \
            ask('Where is located NSRL PRODUCT database?',
                answer_type=str)
        configuration['NSRL']['nsrl_file_db'] = \
            ask('Where is located NSRL FILE database?',
                answer_type=str)

        # write configuration
        config_file = normpath(join(self.install_base, config_file))
        save_config(config_file, configuration)


# ===============
#  Configuration
# ===============

EXCLUDE_FROM_PACKAGES = []
DATA_FILES = {
    # Linux-specific data files
    'linux2': [
        # setup.py related files
        ('', ['setup.py', 'setup.cfg', 'MANIFEST.in', 'requirements.txt']),
        # Celery worker for linux (removed as cannot chmod using setuptools)
        # ('/etc/init.d/',  ['extras/init.d/celeryd.probe']),
        # ('/etc/default/', ['extras/default/celeryd.probe']),
    ]  # IRMA documentation generated with build_sphinx
       + include_data('docs/', base='')
       # IRMA extras files
       + include_data('extras/', base=''),
    'win32': [
        # setup.py related files
        ('', ['setup.py', 'setup.cfg', 'MANIFEST.in', 'requirements.txt']),
        # Celery worker for windows (removed as also removed for linux)
        # (
        #     normpath(join(os.environ.get('APPDATA', ''),
        #                   'irma/irma-probe/services')),
        #     [
        #         'extras/celery/winsrv/celeryd.ini',
        #         'extras/celery/winsrv/service.py'
        #     ]
        # )
    ]  # IRMA documentation generated with build_sphinx
       + include_data('docs/', base='')
       # IRMA extras files
       + include_data('extras/', base=''),
}


# =======
#  Setup
# =======

# NOTE: due to many HACKS, we cannot use setup.py to declare dependencies
# anymore. This should be fixed in the next releases.

setup(
    name='irma-probe-app',
    version='1.1.0',
    url='http://irma.quarkslab.com',
    author='Quarkslab',
    author_email='irma@quarkslab.com',
    description='Probe package application for IRMA',
    license='Apache',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    data_files=DATA_FILES.get(sys.platform, None),
    cmdclass={
        # override sdist so it can call sphinx to build docs
        "sdist": sdist,
        # setup a configure command
        "configure": configure
    },
)
