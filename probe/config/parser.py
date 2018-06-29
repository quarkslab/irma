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
import sys
import logging
import ssl
import multiprocessing

from kombu import Queue
from logging import BASIC_FORMAT, Formatter
from logging.handlers import SysLogHandler
from celery.log import redirect_stdouts_to_logger
from celery.signals import after_setup_task_logger, after_setup_logger
from humanfriendly import parse_size

from irma.common.base.exceptions import IrmaConfigurationError
from irma.common.configuration.ini import TemplatedConfiguration
from irma.common.ftp.sftp import IrmaSFTP
from irma.common.ftp.sftpv2 import IrmaSFTPv2
from irma.common.ftp.ftps import IrmaFTPS
from irma.common.base.utils import common_celery_options


# ==========
#  TEMPLATE
# ==========

template_probe_config = {
    'log': [
        ('syslog', TemplatedConfiguration.integer, 0),
        ('prefix', TemplatedConfiguration.string, "irma-probe :"),
        ('debug', TemplatedConfiguration.boolean, False),
    ],
    'celery_options': [
        ('concurrency', TemplatedConfiguration.integer,
         multiprocessing.cpu_count() * 2),
        ('soft_time_limit', TemplatedConfiguration.integer, 120),
        ('time_limit', TemplatedConfiguration.integer, 200),
    ],
    'broker_probe': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ('ttl', TemplatedConfiguration.integer, 300000)
    ],
    'broker_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ('queue', TemplatedConfiguration.string, None)
    ],
    'ftp': [
        ('protocol', TemplatedConfiguration.string, "sftpv2"),
    ],
    'ftp_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 22),
        ('auth', TemplatedConfiguration.string, "password"),
        ('key_path', TemplatedConfiguration.string, ""),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
    ],
    'ssl_config': [
        ('activate_ssl', TemplatedConfiguration.boolean, False),
        ('ca_certs', TemplatedConfiguration.string, None),
        ('keyfile', TemplatedConfiguration.string, None),
        ('certfile', TemplatedConfiguration.string, None),
    ],
    'probe_list': [
        ('disabled_list', TemplatedConfiguration.string, None),
        ('enabled_list', TemplatedConfiguration.string, None),
    ],
    'probes_config': [
        ('unarchive_max_size', TemplatedConfiguration.string, "5Go"),
        ('unarchive_max_file_size', TemplatedConfiguration.string, "50Mo"),
        ('unarchive_max_files', TemplatedConfiguration.integer, 300),
    ],
}

cwd = os.path.abspath(os.path.dirname(__file__))
cfg_file = os.path.join(cwd, "probe.ini")
probe_config = TemplatedConfiguration(cfg_file, template_probe_config)


# ================
#  Celery helpers
# ================

def get_celery_options(app, app_name):
    concurrency = probe_config.celery_options.concurrency
    soft_time_limit = probe_config.celery_options.soft_time_limit
    time_limit = probe_config.celery_options.time_limit
    options = common_celery_options(app,
                                    app_name,
                                    concurrency,
                                    soft_time_limit,
                                    time_limit)
    if sys.platform.startswith("win32"):
        # use threadpool on windows as workaround
        # of hanging tasks after a while
        options.append('--pool=threads')
        options.append('--logfile=probe_app.log')
    return options


def _conf_celery(app, broker, backend=None, queue=None):
    app.conf.update(BROKER_URL=broker,
                    CELERY_ACCEPT_CONTENT=['json'],
                    CELERY_TASK_SERIALIZER='json',
                    CELERY_RESULT_SERIALIZER='json'
                    )
    if backend is not None:
        app.conf.update(CELERY_RESULT_BACKEND=backend)
        app.conf.update(CELERY_TASK_RESULT_EXPIRES=300)  # 5 minutes
    if queue is not None:
        app.conf.update(CELERY_DEFAULT_QUEUE=queue,
                        # delivery_mode=1 enable transient mode
                        # (don't survive to a server restart)
                        CELERY_QUEUES=(Queue(queue, routing_key=queue),)
                        )
    if probe_config.ssl_config.activate_ssl:
        ca_certs_path = probe_config.ssl_config.ca_certs
        keyfile_path = probe_config.ssl_config.keyfile
        certfile_path = probe_config.ssl_config.certfile

        app.conf.update(
            BROKER_USE_SSL={
               'ca_certs': ca_certs_path,
               'keyfile': keyfile_path,
               'certfile': certfile_path,
               'cert_reqs': ssl.CERT_REQUIRED
            }
        )
    return


def conf_probe_celery(app):
    broker = get_probe_broker_uri()
    _conf_celery(app, broker)


def conf_brain_celery(app):
    broker = get_brain_broker_uri()
    backend = get_brain_backend_uri()
    queue = probe_config.broker_brain.queue
    _conf_celery(app, broker, backend=backend, queue=queue)


# ================
#  Broker helpers
# ================

def _get_broker_uri(broker_config):
    user = broker_config.username
    pwd = broker_config.password
    host = broker_config.host
    port = broker_config.port
    vhost = broker_config.vhost
    return "amqp://{user}:{pwd}@{host}:{port}/{vhost}" \
           "".format(user=user, pwd=pwd, host=host, port=port, vhost=vhost)


def get_probe_broker_uri():
    return _get_broker_uri(probe_config.broker_probe)


def get_brain_broker_uri():
    return _get_broker_uri(probe_config.broker_brain)


# Use AMQP as broker and backend
def get_brain_backend_uri():
    return _get_broker_uri(probe_config.broker_brain)


def get_probe_ttl():
    return probe_config.broker_probe.ttl


# ================
#  Syslog helpers
# ================

def configure_syslog(app):
    if probe_config.log.syslog:
        app.conf.update(CELERYD_LOG_COLOR=False)
        after_setup_logger.connect(setup_log)
        after_setup_task_logger.connect(setup_log)


def setup_log(**args):
    # redirect stdout and stderr to logger
    redirect_stdouts_to_logger(args['logger'])
    # logs to local syslog
    hl = SysLogHandler('/dev/log',
                       facility=SysLogHandler.facility_names['syslog'])
    # setting log level
    hl.setLevel(args['loglevel'])
    # setting log format
    formatter = Formatter(probe_config.log.prefix + BASIC_FORMAT)
    hl.setFormatter(formatter)
    # add new handler to logger
    args['logger'].addHandler(hl)


def debug_enabled():
    return probe_config.log.debug


def setup_debug_logger(logger):
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    FORMAT = "%(asctime)-15s %(name)s %(process)d %(filename)s:"
    FORMAT += "%(lineno)d (%(funcName)s) %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.DEBUG)
    return


# =============
#  FTP helpers
# =============

def get_ftp_class():
    protocol = probe_config.ftp.protocol
    if sys.platform.startswith("win32") and protocol == "sftpv2":
        # sftpv2 is not working on windows
        # http://libssh2-devel.cool.haxx.narkive.com/gPjIsFaS/key-exchange-failure
        # fallback to sftp
        protocol = "sftp"
    if protocol == "sftp":
        key_path = probe_config.ftp_brain.key_path
        auth = probe_config.ftp_brain.auth
        if auth == "key" and not os.path.isfile(key_path):
            msg = "You are using SFTP authentication by key but the path of " \
                  "the private key does not exist:['" + key_path + "']"
            raise IrmaConfigurationError(msg)
        return IrmaSFTP
    elif protocol == "sftpv2":
        auth = probe_config.ftp_brain.auth
        if auth == "key":
            raise IrmaConfigurationError("SFTPv2 pubkey auth not implemented")
        return IrmaSFTPv2
    elif protocol == "ftps":
        return IrmaFTPS


# =========================
#  disabled/enabled helpers
# =========================

def get_disabled_list():
    return probe_config.probe_list.disabled_list


def get_enabled_list():
    return probe_config.probe_list.enabled_list


def check_error_list():
    return (probe_config.probe_list.disabled_list and
            probe_config.probe_list.enabled_list)


# ========
#  Probes
# ========

def get_unpack_limits():
    return (parse_size(probe_config.probes_config.unarchive_max_size),
            parse_size(probe_config.probes_config.unarchive_max_file_size),
            probe_config.probes_config.unarchive_max_files)
