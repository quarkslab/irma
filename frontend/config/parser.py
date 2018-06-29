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
import logging
import ssl

from kombu import Queue
from celery.schedules import crontab

from logging import BASIC_FORMAT, Formatter
from logging.handlers import SysLogHandler
from celery.log import redirect_stdouts_to_logger
from celery.signals import after_setup_task_logger, after_setup_logger

from irma.common.base.utils import common_celery_options
from irma.common.base.exceptions import IrmaConfigurationError
from irma.common.configuration.ini import TemplatedConfiguration
from irma.common.configuration.sql import SQLConf
from irma.common.ftp.sftp import IrmaSFTP
from irma.common.ftp.sftpv2 import IrmaSFTPv2
from irma.common.ftp.ftps import IrmaFTPS

# ==========
#  Template
# ==========

template_frontend_config = {
    'log': [
        ('syslog', TemplatedConfiguration.integer, 0),
        ('prefix', TemplatedConfiguration.string, "irma-frontend :"),
        ('debug', TemplatedConfiguration.boolean, False),
        ('sql_debug', TemplatedConfiguration.boolean, False),
    ],
    'sqldb': [
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
        ('host', TemplatedConfiguration.string, None),
        ('port', TemplatedConfiguration.string, None),
        ('dbname', TemplatedConfiguration.string, None),
        ('tables_prefix', TemplatedConfiguration.string, None),
        ('sslmode', TemplatedConfiguration.string, "disable"),
        ('sslrootcert', TemplatedConfiguration.string, ""),
        ('sslcert', TemplatedConfiguration.string, ""),
        ('sslkey', TemplatedConfiguration.string, ""),
    ],
    'samples_storage': [
        ('path', TemplatedConfiguration.string, None)
    ],
    'celery_brain': [
        ('timeout', TemplatedConfiguration.integer, 60),
    ],
    'celery_options': [
        ('concurrency', TemplatedConfiguration.integer, 0),
        ('soft_time_limit', TemplatedConfiguration.integer, 300),
        ('time_limit', TemplatedConfiguration.integer, 1500),
        ('beat_schedule', TemplatedConfiguration.string,
         "/var/irma/frontend_beat_schedule"),
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
    'ftp': [
        ('protocol', TemplatedConfiguration.string, "sftpv2"),
    ],
    'ftp_brain': [
        ('host', TemplatedConfiguration.string, None),
        ('auth', TemplatedConfiguration.string, "password"),
        ('key_path', TemplatedConfiguration.string, ""),
        ('port', TemplatedConfiguration.integer, 22),
        ('username', TemplatedConfiguration.string, None),
        ('password', TemplatedConfiguration.string, None),
    ],
    'cron_clean_file_age': [
        ('clean_fs_max_age', TemplatedConfiguration.string, "0"),
        ('clean_fs_age_cron_hour', TemplatedConfiguration.string, "0"),
        ('clean_fs_age_cron_minute', TemplatedConfiguration.string, "0"),
        ('clean_fs_age_cron_day_of_week', TemplatedConfiguration.string, "*"),
    ],
    'cron_clean_file_size': [
        ('clean_fs_max_size', TemplatedConfiguration.string, "0"),
        ('clean_fs_size_cron_hour', TemplatedConfiguration.string, "*"),
        ('clean_fs_size_cron_minute', TemplatedConfiguration.string, "0"),
        ('clean_fs_size_cron_day_of_week', TemplatedConfiguration.string, "*"),
    ],
    'interprocess_lock': [
        ('path', TemplatedConfiguration.string,
         "/var/run/lock/irma-frontend.lock"),
        ],
    'ssl_config': [
        ('activate_ssl', TemplatedConfiguration.boolean, False),
        ('ca_certs', TemplatedConfiguration.string, None),
        ('keyfile', TemplatedConfiguration.string, None),
        ('certfile', TemplatedConfiguration.string, None),
    ],
    'processing': [
        ('max_resubmit', TemplatedConfiguration.integer, 15),
    ],
}

config_path = os.environ.get('IRMA_FRONTEND_CFG_PATH')
if config_path is None:
    # Fallback to default path that is
    # current working directory
    config_path = os.path.abspath(os.path.dirname(__file__))

cfg_file = os.path.join(config_path, "frontend.ini")
frontend_config = TemplatedConfiguration(cfg_file, template_frontend_config)


# ===============
#  Celery helper
# ===============

def get_celery_options(app, app_name):
    concurrency = frontend_config.celery_options.concurrency
    soft_time_limit = frontend_config.celery_options.soft_time_limit
    time_limit = frontend_config.celery_options.time_limit
    options = common_celery_options(app,
                                    app_name,
                                    concurrency,
                                    soft_time_limit,
                                    time_limit)
    options.append("--beat")
    beat_schedule = frontend_config.celery_options.beat_schedule
    options.append("--schedule={}".format(beat_schedule))
    return options


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

    if frontend_config.ssl_config.activate_ssl:
        ca_certs_path = frontend_config.ssl_config.ca_certs
        keyfile_path = frontend_config.ssl_config.keyfile
        certfile_path = frontend_config.ssl_config.certfile

        app.conf.update(
            BROKER_USE_SSL={
               'ca_certs': ca_certs_path,
               'keyfile': keyfile_path,
               'certfile': certfile_path,
               'cert_reqs': ssl.CERT_REQUIRED
            }
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
    cron_age_cfg = frontend_config['cron_clean_file_age']
    cron_size_cfg = frontend_config['cron_clean_file_size']
    app.conf.update(
        CELERYBEAT_SCHEDULE={
            # File System clean according to file max age
            'clean_fs_age': {
                'task': 'frontend_app.clean_fs_age',
                'schedule': crontab(
                    hour=cron_age_cfg['clean_fs_age_cron_hour'],
                    minute=cron_age_cfg['clean_fs_age_cron_minute'],
                    day_of_week=cron_age_cfg['clean_fs_age_cron_day_of_week']
                ),
                'args': (),
            },
            # File System clean according to sum max size
            'clean_fs_size': {
                'task': 'frontend_app.clean_fs_size',
                'schedule': crontab(
                    hour=cron_size_cfg['clean_fs_size_cron_hour'],
                    minute=cron_size_cfg['clean_fs_size_cron_minute'],
                    day_of_week=cron_size_cfg['clean_fs_size_cron_day_of_week']
                ),
                'args': (),
            },
        },
        CELERY_TIMEZONE='UTC'
    )


def get_brain_celery_timeout():
    return frontend_config.celery_brain.timeout


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


def sql_debug_enabled():
    return frontend_config.log.sql_debug


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


sqldb = SQLConf(dbms="postgresql", dialect="psycopg2", **frontend_config.sqldb)


def get_samples_storage_path():
    return os.path.abspath(frontend_config.samples_storage.path)


# =============
#  FTP helpers
# =============

def get_ftp_class():
    protocol = frontend_config.ftp.protocol
    if protocol == "sftp":
        key_path = frontend_config.ftp_brain.key_path
        auth = frontend_config.ftp_brain.auth
        if auth == "key" and not os.path.isfile(key_path):
            msg = "You are using SFTP authentication by key but the path of " \
                  "the private key does not exist:['" + key_path + "']"
            raise IrmaConfigurationError(msg)
        return IrmaSFTP
    elif protocol == "sftpv2":
        auth = frontend_config.ftp_brain.auth
        if auth == "key":
            raise IrmaConfigurationError("SFTPv2 pubkey auth not implemented")
        return IrmaSFTPv2
    elif protocol == "ftps":
        return IrmaFTPS


# =====================
#  Concurrency helpers
# =====================

def get_lock_path():
    return frontend_config.interprocess_lock.path


# ====================
#  Processing helpers
# ====================

def get_max_resubmit_level():
    return frontend_config.processing.max_resubmit
