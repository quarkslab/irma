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

import kombu
import shutil
import tempfile
import os
import sys
import config.parser as config
import celery
import logging
import time

from celery import Celery, current_task
from celery.utils.log import get_task_logger
from celery.exceptions import TimeoutError

from irma.common.plugins import PluginManager
from irma.common.utils.utils import bytes_to_utf8
from irma.common.base.exceptions import IrmaTaskError

from probe.controllers.braintasks import register_probe
import probe.controllers.ftpctrl as ftp_ctrl

RETRY_MAX_DELAY = 30

##############################################################################
# celery application configuration
##############################################################################

log = get_task_logger(__name__)

# IRMA specific debug messages are enables through
# config file Section: log / Key: debug
if config.debug_enabled():
    def after_setup_logger_handler(sender=None, logger=None, loglevel=None,
                                   logfile=None, format=None,
                                   colorize=None, **kwds):
        config.setup_debug_logger(logging.getLogger(__name__))
        log.debug("debug is enabled")
    celery.signals.after_setup_logger.connect(after_setup_logger_handler)
    celery.signals.after_setup_task_logger.connect(after_setup_logger_handler)


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
probes = manager.get_all_plugins()
if not probes:
    log.error("No probe found, exiting application")
    sys.exit(1)


# enable (whitelist) disable (blacklist) management
# check if there is a blacklist/whitelist
if config.check_error_list():
    log.error("Enabled and disabled lists are both set, only one is permitted")
    sys.exit(1)
disabled_list = config.get_disabled_list()
enabled_list = config.get_enabled_list()

# add only enabled probes, care default return from split true
if enabled_list:
    allowed_probes = [p for p in probes
                      if p.plugin_name in enabled_list.split(",")]
    probes = allowed_probes

# remove disabled probes, care default return from split true
if disabled_list:
    allowed_probes = [p for p in probes
                      if p.plugin_name not in disabled_list.split(",")]
    probes = allowed_probes

# check if blacklist overkill
if not probes:
    log.error("No probe left, all is disabled")
    sys.exit(1)


queues = []
dlx = kombu.Exchange('dlx', type='direct')
queues.append(kombu.Queue('dlq', exchange=dlx, routing_key='dlq'))
probe_queues_options = {'x-dead-letter-exchange': 'dlx',
                        'x-dead-letter-routing-key': 'dlq',
                        'x-message-ttl': config.get_probe_ttl()}
for p in probes:
    # display successfully loaded plugin
    probe_name = p.plugin_name
    probe_category = p.plugin_category
    exchange_name = probe_name + '_exchange'
    exchange = kombu.Exchange(exchange_name, type='direct')
    log.info(' *** [{category}] Plugin {name} successfully loaded'
             .format(category=probe_category, name=probe_name))
    queues.append(kombu.Queue(probe_name, routing_key=probe_name,
                              exchange=exchange,
                              queue_arguments=probe_queues_options))

log.info('Configure Queues')
# update configuration
probe_app.conf.update(
    CELERY_QUEUES=tuple(queues),
)

for p in probes:
    # register probe on Brain
    log.info('Register probe %s' % p.plugin_name)
    delay = 1
    while True:
        try:
            task = register_probe(p.plugin_name,
                                  p.plugin_display_name,
                                  p.plugin_category,
                                  p.plugin_mimetype_regexp)
            task.get(timeout=10)
            break
        except (TimeoutError, IrmaTaskError):
            log.error("Registering on brain failed retry in %s seconds...",
                      delay)
            time.sleep(delay)
            delay = min([2*delay, RETRY_MAX_DELAY])
            pass

# instantiation of probes and queue creation
probes = dict((probe.plugin_name, probe()) for probe in probes)


##############################################################################
# declare celery tasks
##############################################################################

def handle_output_files(results, frontend, filename):
    # First check if there is some output files
    output_files = results.pop('output_files', None)
    if output_files is None:
        return
    tmpdir = output_files.get('output_dir', None)
    file_list = output_files.get('file_list', None)
    if tmpdir is None or file_list is None:
        return
    uploaded_files = ftp_ctrl.upload_files(frontend, tmpdir, file_list,
                                           filename)
    log.debug("handle_output_files: uploaded %s", ",".join(file_list))
    results['uploaded_files'] = uploaded_files
    shutil.rmtree(tmpdir)
    return


@probe_app.task()
def register():
    routing_key = current_task.request.delivery_info['routing_key']
    probe = probes[routing_key]
    probe_name = type(probe).plugin_name
    probe_display_name = type(probe).plugin_display_name
    probe_category = type(probe).plugin_category
    probe_regexp = type(probe).plugin_mimetype_regexp
    log.debug("queue %s probe %s category %s probe_regexp %s",
              probe_name, probe_display_name, probe_category, probe_regexp)
    register_probe(probe_name, probe_display_name,
                   probe_category, probe_regexp)


@probe_app.task(acks_late=True)
def probe_scan(frontend, filename):
    routing_key = current_task.request.delivery_info['routing_key']
    if routing_key == 'dlq':
        log.error("filename %s scan timeout", filename)
        raise ValueError("Timeout")
    try:
        tmpname = None
        # retrieve queue name and the associated plugin
        probe = probes[routing_key]
        log.debug("filename %s probe %s", filename, probe)
        (fd, tmpname) = tempfile.mkstemp()
        os.close(fd)
        ftp_ctrl.download_file(frontend, filename, tmpname)
        results = probe.run(tmpname)
        handle_output_files(results, frontend, filename)
        return bytes_to_utf8(results)
    except Exception as e:
        log.exception(type(e).__name__ + " : " + str(e))
        raise probe_scan.retry(countdown=2, max_retries=3, exc=e)
    finally:
        # Some AV always delete suspicious file
        if tmpname is not None and os.path.exists(tmpname):
            log.debug("filename %s probe %s removing tmp_name %s",
                      filename, probe, tmpname)
            os.remove(tmpname)


########################
# command line launcher
########################

if __name__ == '__main__':
    options = config.get_celery_options("probe.tasks",
                                        "probe_app")
    probe_app.worker_main(options)
