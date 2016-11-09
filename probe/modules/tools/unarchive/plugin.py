#
# Copyright (c) 2013-2016 Quarkslab.
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
import re
import sys
import tempfile

from datetime import datetime

from lib.common.utils import timestamp
from lib.plugins import PluginBase
from lib.plugin_result import PluginResult
from lib.irma.common.utils import IrmaProbeType
from lib.plugins import ModuleDependency, PlatformDependency, BinaryDependency


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
    _plugin_category_ = "tools"  # TODO add an IrmaProbetype
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
    _plugin_mimetype_regexp = 'archive'

    # =============
    #  constructor
    # =============

    def __init__(self):
        pass

    def unarchive(self, filename, dst_dir):
        Archive = sys.modules['pyunpack'].Archive
        Archive(filename).extractall(dst_dir,
                                     auto_create_dir=True)
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
            results.error = str(e)
        return results
