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
from bottle import Bottle
from lib.irma.common.utils import IrmaFrontendReturn
from lib.plugins import PluginManager

"""
    IRMA FRONTEND WEB API
    defines all accessible route accessed via uwsgi..
"""

# discover plugins located at specified path
plugin_path = os.path.abspath("frontend/api/modules")
if not os.path.exists(plugin_path):
    print("path {0} is invalid, cannot load api plugin".format(plugin_path))
    sys.exit(1)
manager = PluginManager()
manager.discover(plugin_path)

# main bottle app
application = Bottle()

# now discover plugins installed
plugins = PluginManager().get_all_plugins()
if not plugins:
    print("No api plugins found")
else:
    for plugin in plugins:
        mount_path = plugin().get_mount_path()
        app = plugin().get_app()
        print "Found app {0} to mount @ {1}".format(mount_path,
                                                    app)
        application.mount(mount_path, app)


# =============
#  Server root
# =============

@application.route("/ping")
def svr_index():
    """ hello world

    :route: /
    :rtype: dict of 'code': int, 'msg': str
    :return: success
    """
    return IrmaFrontendReturn.success()
