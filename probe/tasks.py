#
# Copyright (c) 2013-2015 QuarksLab.
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
import shutil
import tempfile
import os
import sys
import uuid
import config.parser as config

from celery import Celery, current_task
from celery.utils.log import get_task_logger
from celery.exceptions import TimeoutError

from lib.irma.ftp.handler import FtpTls
from lib.plugins import PluginManager
from lib.common.utils import to_unicode

from probe.controllers.braintasks import register_probe

##############################################################################
# celery application configuration
##############################################################################

log = get_task_logger(__name__)

# disable insecure serializer (disabled by default from 3.x.x)
if (kombu.VERSION.major) < 3:
    kombu.disable_insecure_serializers()

# declare a new Local Probe application
probe_app = Celery("probe.tasks")
config.conf_probe_celery(probe_app)
config.configure_syslog(probe_app)

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


queues = []
for p in probes:
    # display successfully loaded plugin
    probe_name = p.plugin_name
    probe_category = p.plugin_category
    log.info(' *** [{category}] Plugin {name} successfully loaded'
             .format(category=probe_category, name=probe_name))
    queues.append(kombu.Queue(probe_name, routing_key=probe_name))

log.info('Configure Queues')
# update configuration
probe_app.conf.update(
    CELERY_QUEUES=tuple(queues),
)

for p in probes:
    # register probe on Brain
    probe_name = p.plugin_name
    probe_category = p.plugin_category
    mimetype_regexp = p.plugin_mimetype_regexp
    log.info('Register probe %s' % probe_name)
    try_nb = 1
    while True:
        try:
            try_nb += 1
            task = register_probe(probe_name, probe_category, mimetype_regexp)
            task.get(timeout=10)
            break
        except TimeoutError:
            log.info("Registering on brain try %s", format(try_nb))
            pass

# instanciation of probes and queue creation
probes = dict((probe.plugin_name, probe()) for probe in probes)


##############################################################################
# declare celery tasks
##############################################################################

def handle_output_files(results, dstpath):
    # First check if there is some output files
    output_files = results.pop('output_files', None)
    if output_files is None:
        return
    tmpdir = output_files.get('output_dir', None)
    file_list = output_files.get('file_list', None)
    log.debug("handle_output_files with %s", ",".join(file_list))
    if tmpdir is None or file_list is None:
        return
    conf_ftp = config.probe_config.ftp_brain
    uploaded_files = {}
    with FtpTls(conf_ftp.host,
                conf_ftp.port,
                conf_ftp.username,
                conf_ftp.password) as ftps:
        for path in file_list:
            if os.path.isdir(path):
                continue
            log.debug("handle_output_files uploading %s", path)
            full_path = os.path.join(tmpdir, path)
            hashname = ftps.upload_file(dstpath, full_path)
            uploaded_files[path] = hashname
    results['uploaded_files'] = uploaded_files
    shutil.rmtree(tmpdir)
    return


@probe_app.task()
def register():
    routing_key = current_task.request.delivery_info['routing_key']
    probe = probes[routing_key]
    probe_name = type(probe).plugin_name
    probe_category = type(probe).plugin_category
    probe_regexp = type(probe).plugin_mimetype_regexp
    register_probe(probe_name, probe_category, probe_regexp)


@probe_app.task(acks_late=True)
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
        handle_output_files(results, path)
        return to_unicode(results)
    except Exception as e:
        log.exception("Exception has occured: {0}".format(e))
        raise probe_scan.retry(countdown=2, max_retries=3, exc=e)

##############################################################################
# command line launcher, only for debug purposes
##############################################################################

if __name__ == '__main__':
    probe_app.worker_main([
        '--app=probe.tasks:probe_app',  # app instance to use
        '-l', 'info',             # logging level
        '--without-gossip',       # do not subscribe to other workers events.
        '--without-mingle',       # do not synchronize with
                                  # other workers at startup
        '--without-heartbeat',    # do not send event heartbeats
        '-nprobe-{0}'.format(uuid.uuid4())   # unique id
    ])
