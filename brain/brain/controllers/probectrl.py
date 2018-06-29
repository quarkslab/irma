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
import time

import config.parser as config
from celery import Celery
from fasteners import interprocess_locked
from brain.models.sqlobjects import Probe
import brain.controllers.probetasks as celery_probe
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
cache_probelist = manager.dict()

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


# as the method for querying active_queues is not forksafe
# insure there is only one call running at a time
# among the different workers
@interprocess_locked(interprocess_lock_path)
def active_probes():
    global cache_probelist
    # get active queues list from probe celery app
    log.debug("cache_probelist: %s id: %x", cache_probelist,
              id(cache_probelist))
    now = time.time()
    cache_time = list(cache_probelist.values())
    if len(cache_time) != 0:
        cache_age = now - min(cache_time)
        log.debug("cache age: %s", cache_age)
    if len(cache_time) == 0 or cache_age > PROBELIST_CACHE_TIME:
        log.debug("refreshing cached list")
        cache_probelist.clear()
        # scan all active queues except result queue
        # to list all probes queues ready
        queues = probe_app.control.inspect().active_queues()
        if queues:
            result_queue = config.brain_config['broker_probe'].queue
            for queuelist in queues.values():
                for queue in queuelist:
                    # exclude only predefined result queue
                    if queue['name'] != result_queue:
                        # Store name and time to have a
                        # list cache per queue
                        # TODO updated on success result
                        probe = queue['name']
                        log.info("add/refresh probe %s cache %s", probe, now)
                        cache_probelist.update({probe: now})
    probelist = sorted(cache_probelist.keys())
    log.debug("probe_list: %s", "-".join(probelist))
    return probelist


def refresh_probes(session):
    """ Put all probes offline and send them a register request
        Infos/Online state will be updated
    """
    probes = Probe.all(session)
    for probe in probes:
        probe.online = False
    for active_probe in active_probes():
        celery_probe.get_info(active_probe)
    return


def get_list(session):
    """ Return a list of probe name (queues name)
        that a scan could use
    """
    active_probes_list = active_probes()
    probes = Probe.all(session)
    # Update Status
    for probe in probes:
        if probe.name not in active_probes_list:
            log.debug("probe list set %s offline", probe.name)
            probe.online = False
        elif probe.online is False:
            log.debug("probe list set %s online", probe.name)
            probe.online = True
    probes_list = [p.name for p in probes if p.online]
    log.info("probe list %s", "-".join(probes_list))
    return probes_list


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
