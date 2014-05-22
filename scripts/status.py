#
# Copyright (c) 2014 QuarksLab.
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

#!/usr/bin/env python

import config.parser as config
from celery import Celery

import pymongo
import amqp
import requests
import libvirt

FRONTEND_TEST_URL = "http://frontend.irma.qb/"
FRONTEND_API_TEST_URL = "http://frontend.irma.qb/_api/probe/list"


scan_app = Celery('scan')
config.conf_brain_celery(scan_app)

probe_app = Celery('probe')
config.conf_probe_celery(probe_app)

frontend_app = Celery('frontend')
config.conf_frontend_celery(frontend_app)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

status_ok = 0
status_ko = 1
status_str = [bcolors.OKGREEN + "[+]" + bcolors.ENDC,
              bcolors.FAIL + "[-]" + bcolors.ENDC]


def print_hdr(msg):
    print
    print bcolors.HEADER + "## {0} ##".format(msg) + bcolors.ENDC
    print


def print_msg(code_msg_list):
    for (status, line) in code_msg_list:
        print '\t',
        print status_str[status], line


def ping_celery_app(celery):
    try:
        res = []
        ping_status = celery.control.ping(timeout=0.5)
        if len(ping_status) == 0:
            res.append((status_ko,
                        'celery app {0} is down'.format(celery.main)))
        for r in ping_status:
            for host, response in r.items():
                if response['ok'] == u'pong':
                    msg = 'celery app {0} is up'.format(host)
                    res.append((status_ok, msg))
                else:
                    msg = 'celery app {0} is down'.format(host)
                    res.append((status_ko, msg))
        queues = celery.control.inspect().active_queues()
        for (host, infolist) in queues.items():
            queuenames = "-".join([info['name'] for info in infolist])
            msg = '\t| {0} queue {1}'.format(host, queuenames)
            res.append((status_ok, msg))
    except:
        url = celery.conf['BROKER_URL']
        msg = "no celery running perhaps broker is down on {0}".format(url)
        res.append((status_ko, msg))
    return res


def ping_db(uri):
    try:
        pymongo.Connection(uri)
        return [(status_ok, 'mongodb {0} is up and runnning'.format(uri))]
    except:
        return [(status_ko, 'mongodb {0} is down'.format(uri))]


def ping_rabbitmq(address, port, usr, pwd, vhost):
    try:
        host = '{address}:{port}'.format(address=address, port=port)
        amqp.Connection(host=host,
                        userid=usr,
                        password=pwd,
                        virtual_host=vhost)
        msg = "rabbitmq vhost {0} on {1} is up".format(vhost,
                                                       address)
        return [(status_ok, msg)]
    except:
        msg = 'rabbitmq vhost {0} on {1} is down'.format(vhost,
                                                         address)
        return [(status_ko, msg)]


def ping_frontend(url):
    try:
        requests.get(url=url)
        return [(status_ok, 'frontend {0} is up and runnning'.format(url))]
    except:
        return [(status_ko, 'frontend {0} is down'.format(url))]


def ping_libvirt(uri):
    try:
        libvirt.open(uri)
        return [(status_ok, 'libvirt {0} is up and runnning'.format(uri))]
    except:
        return [(status_ko, 'libvirt {0} is down'.format(uri))]
    return

print_hdr("RabbitMQ")
for broker in ['broker_brain', 'broker_probe', 'broker_frontend']:
    print_msg(ping_rabbitmq(config.brain_config[broker].host,
                            config.brain_config[broker].port,
                            config.brain_config[broker].username,
                            config.brain_config[broker].password,
                            config.brain_config[broker].vhost))

print_hdr("Frontend")
print_msg(ping_frontend(FRONTEND_TEST_URL))

print_hdr("Frontend Api")
print_msg(ping_frontend(FRONTEND_API_TEST_URL))

print_hdr("Celery")
for app in [scan_app, probe_app, frontend_app]:
    print_msg(ping_celery_app(app))
print
