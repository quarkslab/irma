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

import logging
import re
import multiprocessing

import config.parser as config
from celery import Celery
from fasteners import interprocess_locked
from brain.models.sqlobjects import Probe
from irma.common.base.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError
from irma.common.plugin_result import PluginResult

log = logging.getLogger(__name__)


probe_app = Celery('probetasks')
config.conf_probe_celery(probe_app)
config.configure_syslog(probe_app)

# Time to cache the probe list
# to avoid asking to rabbitmq
PROBELIST_CACHE_TIME = 30
manager = multiprocessing.Manager()
available_probes = manager.list()

interprocess_lock_path = config.get_lock_path()


def register(name, display_name, category, mimetype_regexp, session):
    try:
        probe = Probe.get_by_name(name, session)
        log.info("probe %s already registred "
                 "updating parameters: "
                 "[display_name:%s cat:%s regexp:%s]",
                 name, display_name, category, mimetype_regexp)
        session.query(Probe)\
            .filter_by(id=probe.id)\
            .update({'category': category, 'mimetype_regexp': mimetype_regexp,
                     'online': True, 'display_name': display_name})
    except IrmaDatabaseResultNotFound:
        log.info("register probe %s"
                 " with parameters: "
                 "[display_name:%s cat:%s regexp:%s]",
                 name, display_name, category, mimetype_regexp)
        probe = Probe(name=name,
                      display_name=display_name,
                      category=category,
                      mimetype_regexp=mimetype_regexp,
                      online=True)
        session.add(probe)
        return


def mimetype_probelist(mimetype, session):
    log.debug("asking what probes handle %s", mimetype)
    probe_list = []
    for p in Probe.all(session):
        regexp = p.mimetype_regexp
        if regexp is None or \
           re.search(regexp, mimetype, re.IGNORECASE) is not None:
            probe_list.append(p.name)
    log.debug("probes: %s", "-".join(probe_list))
    return probe_list


@interprocess_locked(interprocess_lock_path)
def refresh_probelist(session):
    global available_probes
    dbprobes = Probe.all(session)
    result_queue_name = config.brain_config['broker_probe'].queue
    queues = probe_app.control.inspect().active_queues() or {}
    queues = [q['name'] for ql in queues.values()
              for q in ql if q['name'] != result_queue_name]

    for probe in dbprobes:
        if probe.online and probe.name not in queues:
            log.debug("probelist set %s offline", probe.name)
            probe.online = False
            try:
                available_probes.remove(probe.name)
            except ValueError:
                pass
        elif (not probe.online or probe.name not in available_probes) \
                and probe.name in queues:
            log.debug("probelist set %s online", probe.name)
            probe.online = True
            available_probes.append(probe.name)


def create_error_results(probename, error, session):
    try:
        probe = Probe.get_by_name(probename, session)
        display_name = probe.display_name
        category = probe.category
    except IrmaDatabaseError:
        display_name = probename
        category = "unknown"
    result = PluginResult(name=display_name, type=category, error=error)
    return result
