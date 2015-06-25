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

import os

from kombu import Queue
from logging import BASIC_FORMAT, Formatter
from logging.handlers import SysLogHandler
from celery.log import redirect_stdouts_to_logger
from celery.signals import after_setup_task_logger, after_setup_logger
from lib.irma.configuration.ini import TemplatedConfiguration


# ==========
#  TEMPLATE
# ==========

template_brain_config = {
    'log': [
        ('syslog', TemplatedConfiguration.integer, 0),
        ('prefix', TemplatedConfiguration.string, "irma-brain :"),
    ],
    'broker_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ('queue', TemplatedConfiguration.string, None)
        ],
    'broker_probe': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ('queue', TemplatedConfiguration.string, None)
        ],
    'broker_frontend': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ('queue', TemplatedConfiguration.string, None)
        ],
    'sqldb': [
        ('dbms', TemplatedConfiguration.string, None),
        ('dialect', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ('host', TemplatedConfiguration.string, None),
        ('dbname', TemplatedConfiguration.string, None),
        ('tables_prefix', TemplatedConfiguration.string, None),
    ],
    'ftp_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 21),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ]
    }

config_path = os.environ.get('IRMA_BRAIN_CFG_PATH')
if config_path is None:
    # Fallback to default path that is
    # current working directory
    config_path = os.path.abspath(os.path.dirname(__file__))

cfg_file = "{0}/{1}".format(config_path, "brain.ini")
brain_config = TemplatedConfiguration(cfg_file, template_brain_config)


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
    return


def conf_brain_celery(app):
    broker = get_brain_broker_uri()
    # default backend is amqp
    # same as broker
    backend = get_brain_backend_uri()
    queue = brain_config.broker_brain.queue
    _conf_celery(app, broker, backend=backend, queue=queue)


def conf_probe_celery(app):
    broker = get_probe_broker_uri()
    _conf_celery(app, broker, backend=False)


def conf_frontend_celery(app):
    broker = get_frontend_broker_uri()
    queue = brain_config.broker_frontend.queue
    _conf_celery(app, broker, backend=False, queue=queue)


def conf_results_celery(app):
    broker = get_probe_broker_uri()
    queue = brain_config.broker_probe.queue
    _conf_celery(app, broker, backend=False, queue=queue)


# =================
#  Brocker helpers
# =================

def _get_amqp_uri(broker_config):
    user = broker_config.username
    pwd = broker_config.password
    host = broker_config.host
    port = broker_config.port
    vhost = broker_config.vhost
    return "amqp://{user}:{pwd}@{host}:{port}/{vhost}" \
           "".format(user=user, pwd=pwd, host=host, port=port, vhost=vhost)


def get_brain_broker_uri():
    return _get_amqp_uri(brain_config.broker_brain)


def get_brain_backend_uri():
    return _get_amqp_uri(brain_config.broker_brain)


def get_probe_broker_uri():
    return _get_amqp_uri(brain_config.broker_probe)


def get_frontend_broker_uri():
    return _get_amqp_uri(brain_config.broker_frontend)


def get_frontend_rmqvhost():
    return brain_config.broker_frontend.vhost


# ================
#  Syslog helpers
# ================

def configure_syslog(app):
    if brain_config.log.syslog:
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
    formatter = Formatter(brain_config.log.prefix + BASIC_FORMAT)
    hl.setFormatter(formatter)
    # add new handler to logger
    args['logger'].addHandler(hl)


# ==================
#  Database helpers
# ==================

def get_sql_db_uri_params():
    return (
        brain_config.sqldb.dbms,
        brain_config.sqldb.dialect,
        brain_config.sqldb.username,
        brain_config.sqldb.password,
        brain_config.sqldb.host,
        brain_config.sqldb.dbname,
    )


def get_sql_db_tables_prefix():
    return brain_config.sqldb.tables_prefix
