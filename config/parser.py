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
import logging
import ssl

from kombu import Queue
from logging import BASIC_FORMAT, Formatter
from logging.handlers import SysLogHandler
from celery.log import redirect_stdouts_to_logger
from celery.signals import after_setup_task_logger, after_setup_logger
from lib.irma.configuration.ini import TemplatedConfiguration
from lib.irma.ftp.sftp import IrmaSFTP
from lib.irma.ftp.ftps import IrmaFTPS


# ==========
#  TEMPLATE
# ==========

template_probe_config = {
    'log': [
        ('syslog', TemplatedConfiguration.integer, 0),
        ('prefix', TemplatedConfiguration.string, "irma-probe :"),
        ('debug', TemplatedConfiguration.boolean, False),
    ],
    'broker_probe': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None)
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
        ('protocol', TemplatedConfiguration.string, "sftp"),
    ],
    'ftp_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 22),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
    ],
    'ssl_config': [
        ('activate_ssl', TemplatedConfiguration.boolean, False),
        ('ca_certs', TemplatedConfiguration.string, None),
        ('keyfile', TemplatedConfiguration.string, None),
        ('certfile', TemplatedConfiguration.string, None),
    ],
}

cwd = os.path.abspath(os.path.dirname(__file__))
cfg_file = os.path.join(cwd, "probe.ini")
probe_config = TemplatedConfiguration(cfg_file, template_probe_config)


# ================
#  Celery helpers
# ================

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
        ca_certs = probe_config.ssl_config.ca_certs
        keyfile = probe_config.ssl_config.keyfile
        certfile = probe_config.ssl_config.certfile

        ssl_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                os.path.pardir))
        ca_certs_path = '{ssl_path}/ssl/{ca_certs}'.format(ca_certs=ca_certs,
                                                           ssl_path=ssl_path)
        keyfile_path = '{ssl_path}/ssl/{keyfile}'.format(keyfile=keyfile,
                                                         ssl_path=ssl_path)
        certfile_path = '{ssl_path}/ssl/{certfile}'.format(certfile=certfile,
                                                           ssl_path=ssl_path)
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
    broker = get_brain_backend_uri()
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
    if protocol == "sftp":
        return IrmaSFTP
    elif protocol == "ftps":
        return IrmaFTPS
