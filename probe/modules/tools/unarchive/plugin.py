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

import os
import shutil
import sys
import tempfile
import resource
from datetime import datetime
import config.parser as config
from irma.common.utils.utils import timestamp
from irma.common.plugins import PluginBase
from irma.common.plugin_result import PluginResult
from irma.common.base.utils import IrmaProbeType
from irma.common.plugins import ModuleDependency, PlatformDependency, \
    BinaryDependency


class UnarchivePlugin(PluginBase):

    class UnarchiveResult:
        ERROR = -1
        OK = 0

    # =================
    #  plugin metadata
    # =================

    _plugin_name_ = "Unarchive"
    _plugin_display_name_ = "Unarchive"
    _plugin_author_ = "Quarkslab"
    _plugin_version_ = "1.0.0"
    _plugin_category_ = IrmaProbeType.tools
    _plugin_description_ = "Plugin to unarchive files"
    _plugin_dependencies_ = [
        PlatformDependency('linux'),
        ModuleDependency(
            'pyunpack',
            help='See requirements.txt for needed dependencies'
        ),
        BinaryDependency(
            'patool',
            help='unarchiver frontend required to support various formats'
        ),
    ]
    _plugin_mimetype_regexp = 'archive|compressed'

    # =============
    #  constructor
    # =============

    def __init__(self):
        pass

    def unarchive(self, filename, dst_dir):
        limit_data, limit_fsize, limit_nofile = config.get_unpack_limits()
        soft_as, hard_as = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (limit_data, hard_as))
        soft_data, hard_data = resource.getrlimit(resource.RLIMIT_DATA)
        resource.setrlimit(resource.RLIMIT_DATA, (limit_data, hard_data))
        soft_stack, hard_stack = resource.getrlimit(resource.RLIMIT_STACK)
        resource.setrlimit(resource.RLIMIT_STACK, (limit_data, hard_stack))
        soft_fsize, hard_fsize = resource.getrlimit(resource.RLIMIT_FSIZE)
        resource.setrlimit(resource.RLIMIT_FSIZE, (limit_fsize, hard_fsize))
        soft_nofile, hard_nofile = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (limit_nofile, hard_nofile))
        Archive = sys.modules['pyunpack'].Archive
        try:
            Archive(filename).extractall(dst_dir,
                                         auto_create_dir=True)
        except Exception:
            shutil.rmtree(dst_dir)
            raise
        finally:
            resource.setrlimit(resource.RLIMIT_AS, (soft_as, hard_as))
            resource.setrlimit(resource.RLIMIT_DATA, (soft_data, hard_data))
            resource.setrlimit(resource.RLIMIT_STACK, (soft_stack, hard_stack))
            resource.setrlimit(resource.RLIMIT_FSIZE, (soft_fsize, hard_fsize))
            resource.setrlimit(resource.RLIMIT_NOFILE,
                               (soft_nofile, hard_nofile))

        path_list = []
        # Make sure dst_dir ends with a '/'
        # useful when removing from filepath
        if len(dst_dir) > 1 and dst_dir[-1] != '/':
            dst_dir += '/'
        for (dirname, _, filenames) in os.walk(dst_dir):
            for filename in filenames:
                relative_dirname = dirname.replace(dst_dir, "")
                path = os.path.join(relative_dirname, filename)
                path_list.append(path)
        return path_list

    # ==================
    #  probe interfaces
    # ==================

    def run(self, paths):
        results = PluginResult(name=type(self).plugin_name,
                               type=type(self).plugin_category,
                               version=None)
        try:
            started = timestamp(datetime.utcnow())
            output_dir = tempfile.mkdtemp()
            file_list = self.unarchive(paths, output_dir)
            results.output_files = {}
            results.output_files['output_dir'] = output_dir
            results.output_files['file_list'] = file_list
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started
            results.status = self.UnarchiveResult.OK
            results.results = None
        except Exception as e:
            results.status = self.UnarchiveResult.ERROR
            results.error = "Maybe a zip bomb : " + str(e)
        return results
