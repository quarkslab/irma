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
import logging

from kombu import Queue
from celery.schedules import crontab

from logging import BASIC_FORMAT, Formatter
from logging.handlers import SysLogHandler
from celery.log import redirect_stdouts_to_logger
from celery.signals import after_setup_task_logger, after_setup_logger

from lib.irma.configuration.ini import TemplatedConfiguration


# ==========
#  Template
# ==========

template_frontend_config = {
    'log': [
        ('syslog', TemplatedConfiguration.integer, 0),
        ('prefix', TemplatedConfiguration.string, "irma-frontend :"),
        ('debug', TemplatedConfiguration.boolean, False),
    ],
    'mongodb': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 27017),
        ('dbname', TemplatedConfiguration.string, None),
        ('collections_prefix', TemplatedConfiguration.string, None),
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
    'samples_storage': [
        ('path', TemplatedConfiguration.string, None)
    ],
    'celery_brain': [
        ('timeout', TemplatedConfiguration.integer, 60),
    ],
    'celery_frontend': [
        ('timeout', TemplatedConfiguration.integer, 30),
    ],
    'broker_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ('queue', TemplatedConfiguration.string, None),
    ],
    'broker_frontend': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 5672),
        ('vhost', TemplatedConfiguration.string, None),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ('queue', TemplatedConfiguration.string, None),
    ],
    'ftp_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.integer, 21),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
    ],
    'cron_frontend': [
        ('clean_db_file_max_age', TemplatedConfiguration.integer, 0),
        ('clean_db_cron_hour', TemplatedConfiguration.string, '0'),
        ('clean_db_cron_minute', TemplatedConfiguration.string, '0'),
        ('clean_db_cron_day_of_week', TemplatedConfiguration.string, '*'),
    ],
}

config_path = os.environ.get('IRMA_FRONTEND_CFG_PATH')
if config_path is None:
    # Fallback to default path that is
    # current working directory
    config_path = os.path.abspath(os.path.dirname(__file__))

cfg_file = "{0}/{1}".format(config_path, "frontend.ini")
frontend_config = TemplatedConfiguration(cfg_file, template_frontend_config)


# ===============
#  Celery helper
# ===============

def _conf_celery(app, broker, backend=None, queue=None):
    app.conf.update(
        BROKER_URL=broker,
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json'
        )
    if backend is not None:
        app.conf.update(CELERY_RESULT_BACKEND=backend)
        app.conf.update(CELERY_TASK_RESULT_EXPIRES=300)  # 5 minutes

    if queue is not None:
        app.conf.update(
            CELERY_DEFAULT_QUEUE=queue,
            # delivery_mode=1 enable transient mode
            # (don't survive to a server restart)
            CELERY_QUEUES=(Queue(queue, routing_key=queue),)
            )
    return


def conf_brain_celery(app):
    broker = get_brain_broker_uri()
    # default backend for brain celery
    # is amqp
    backend = get_brain_backend_uri()
    queue = frontend_config.broker_brain.queue
    _conf_celery(app, broker, backend=backend, queue=queue)


def conf_frontend_celery(app):
    broker = get_frontend_broker_uri()
    queue = frontend_config.broker_frontend.queue
    _conf_celery(app, broker, queue=queue)
    # add celerybeat conf only for frontend app
    cron_cfg = frontend_config['cron_frontend']
    app.conf.update(
        CELERYBEAT_SCHEDULE={
            # Database clean
            'clean_db': {
                'task': 'frontend.tasks.clean_db',
                'schedule': crontab(
                    hour=cron_cfg['clean_db_cron_hour'],
                    minute=cron_cfg['clean_db_cron_minute'],
                    day_of_week=cron_cfg['clean_db_cron_day_of_week']
                ),
                'args': (),
            },
        },
        CELERY_TIMEZONE='UTC'
    )


def get_brain_celery_timeout():
    return frontend_config.celery_brain.timeout


def get_frontend_celery_timeout():
    return frontend_config.celery_admin.timeout


# ========================
#  Broker/Backend helpers
# ========================

def _get_amqp_uri(broker_config):
    user = broker_config.username
    pwd = broker_config.password
    host = broker_config.host
    port = broker_config.port
    vhost = broker_config.vhost
    return "amqp://{user}:{pwd}@{host}:{port}/{vhost}".format(user=user,
                                                              pwd=pwd,
                                                              host=host,
                                                              port=port,
                                                              vhost=vhost)


def get_brain_broker_uri():
    return _get_amqp_uri(frontend_config.broker_brain)


def get_brain_backend_uri():
    return _get_amqp_uri(frontend_config.broker_brain)


def get_frontend_broker_uri():
    return _get_amqp_uri(frontend_config.broker_frontend)


# ================
#  Syslog helpers
# ================

def configure_syslog(app):
    if frontend_config.log.syslog:
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
    formatter = Formatter(frontend_config.log.prefix + BASIC_FORMAT)
    hl.setFormatter(formatter)
    # add new handler to logger
    args['logger'].addHandler(hl)


def debug_enabled():
    return frontend_config.log.debug


def setup_debug_logger(logger):
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    FORMAT = "%(asctime)-15s %(name)s %(process)d %(filename)s:"
    FORMAT += "%(lineno)d (%(funcName)s) %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.DEBUG)
    return


# ==================
#  Database helpers
# ==================

def get_db_uri():
    host = frontend_config.mongodb.host
    port = frontend_config.mongodb.port
    return "mongodb://{host}:{port}/".format(host=host, port=port)


def get_nosql_db_collections_prefix():
    return frontend_config.mongodb.collections_prefix


def get_sql_db_uri_params():
    return (
        frontend_config.sqldb.dbms,
        frontend_config.sqldb.dialect,
        frontend_config.sqldb.username,
        frontend_config.sqldb.password,
        frontend_config.sqldb.host,
        frontend_config.sqldb.dbname,
    )


def get_sql_url():
    dbms = frontend_config.sqldb.dbms
    if frontend_config.sqldb.dialect:
        dbms = "{0}+{1}".format(dbms, frontend_config.sqldb.dialect)
    host_and_id = ''
    if frontend_config.sqldb.host and frontend_config.sqldb.username:
        if frontend_config.sqldb.password:
            host_and_id = "{0}:{1}@{2}".format(frontend_config.sqldb.username,
                                               frontend_config.sqldb.password,
                                               frontend_config.sqldb.host)
        else:
            host_and_id = "{0}@{1}".format(frontend_config.sqldb.username,
                                           frontend_config.sqldb.host)
    url = "{0}://{1}/{2}".format(dbms,
                                 host_and_id,
                                 frontend_config.sqldb.dbname)
    return url


def get_sql_db_tables_prefix():
    return frontend_config.sqldb.tables_prefix


def get_samples_storage_path():
    return os.path.abspath(frontend_config.samples_storage.path)
