#
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

import sys
import argparse
import pprint
import logging

from irma.common.plugins import PluginManager
from irma.common.utils.utils import bytes_to_utf8


def lookup_modules():
    manager = PluginManager()
    manager.discover("modules")
    modules = manager.get_all_plugins()
    return dict(map(lambda cls: (cls.plugin_name, cls), modules))


def execute_module(module, *args):
    instance = module()
    return instance.run(*args)


if __name__ == '__main__':

    # lookup modules
    modules = lookup_modules()

    # define command line arguments
    parser = argparse.ArgumentParser(description='Module debug CLI')
    parser.add_argument('module', type=str, choices=modules.keys(),
                        help='module to execute')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('filename', type=str, nargs='+',
                        help='name of the file to run against this module')
    args = parser.parse_args()

    # set verbosity
    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    # execute module and print results
    for filename in args.filename:
        results = execute_module(modules[args.module], filename)
        results = bytes_to_utf8(results)
        print("{0}".format(pprint.pformat(results)))
