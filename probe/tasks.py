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

import kombu
import ssl
import tempfile
import os
import sys
import uuid
import config.parser as config

from celery import Celery, current_task
from celery.utils.log import get_task_logger

from lib.irma.ftp.handler import FtpTls
from lib.plugins import PluginManager
from lib.common.utils import to_unicode

##############################################################################
# celery application configuration
##############################################################################

log = get_task_logger(__name__)

# disable insecure serializer (disabled by default from 3.x.x)
if (kombu.VERSION.major) < 3:
    kombu.disable_insecure_serializers()

# declare a new application
app = Celery("probe.tasks")
config.conf_probe_celery(app)
config.configure_syslog(app)

# discover plugins located at specified path
plugin_path = os.path.abspath("modules")
if not os.path.exists(plugin_path):
    log.error("path {0} is invalid, cannot load probes".format(plugin_path))
    sys.exit(1)
manager = PluginManager()
manager.discover(plugin_path)

# determine dynamically queues to connect to using plugin names
probes = PluginManager().get_all_plugins()
if not probes:
    log.error("No probe found, exiting application")
    sys.exit(1)

# display successfully loaded plugin
for p in probes:
    log.warn(' *** [{category}] Plugin {name} successfully loaded'
             .format(category=p.plugin_category, name=p.plugin_name))

# instanciation of probes and queue creation
probes = dict((probe.plugin_name, probe()) for probe in probes)
queues = []
for probe in probes.keys():
    queues.append(kombu.Queue(probe, routing_key=probe))

# update configuration
app.conf.update(
    CELERY_QUEUES=tuple(queues),
)


##############################################################################
# declare celery tasks
##############################################################################

@app.task(acks_late=True)
def probe_scan(frontend, scanid, filename):
    try:
        # retrieve queue name and the associated plugin
        routing_key = current_task.request.delivery_info['routing_key']
        probe = probes[routing_key]
        conf_ftp = config.probe_config.ftp_brain
        (fd, tmpname) = tempfile.mkstemp()
        os.close(fd)
        with FtpTls(conf_ftp.host,
                    conf_ftp.port,
                    conf_ftp.username,
                    conf_ftp.password) as ftps:
            path = "{0}/{1}".format(frontend, scanid)
            ftps.download(path, filename, tmpname)
        results = probe.run(tmpname)
        # Some AV always delete suspicious file
        if os.path.exists(tmpname):
            os.remove(tmpname)
        return to_unicode(results)
    except Exception as e:
        log.exception("Exception has occured: {0}".format(e))
        raise probe_scan.retry(countdown=2, max_retries=3, exc=e)

##############################################################################
# command line launcher, only for debug purposes
##############################################################################

if __name__ == '__main__':
    app.worker_main([
        '--app=probe.tasks:app',  # app instance to use
        '-l', 'info',             # logging level
        '--without-gossip',       # do not subscribe to other workers events.
        '--without-mingle',       # do not synchronize with
                                  # other workers at startup
        '--without-heartbeat',    # do not send event heartbeats
        '-nprobe-{0}'.format(uuid.uuid4())   # unique id
    ])
