import os
from celery.schedules import crontab
from kombu import Queue
from lib.irma.configuration.ini import TemplatedConfiguration
# ______________________________________________________________________________ TEMPLATE

template_frontend_config = {
                         'mongodb': [('host', TemplatedConfiguration.string, None),
                                      ('port', TemplatedConfiguration.integer, 27017),
                                      ('dbname', TemplatedConfiguration.string, None),
                                    ],
                         'collections': [('scan_info', TemplatedConfiguration.string, None),
                                          ('scan_results', TemplatedConfiguration.string, None),
                                          ('scan_files', TemplatedConfiguration.string, None),
                                          ('scan_file_fs', TemplatedConfiguration.string, None),
                                         ],
                         'celery_brain': [('timeout', TemplatedConfiguration.integer, 10),
                                          ],
                         'celery_frontend': [('timeout', TemplatedConfiguration.integer, 10),
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
                         'backend_brain': [
                                   ('host', TemplatedConfiguration.string, None),
                                   ('port', TemplatedConfiguration.integer, 6379),
                                   ('db', TemplatedConfiguration.integer, None),
                                   ],
                         'ftp_brain': [
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 21),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password', TemplatedConfiguration.string, None),
                                    ],
                        'clean_db': [
                                    ('scan_info_max_age', TemplatedConfiguration.integer, 3600),  # in seconds
                                    ('cron_hour', TemplatedConfiguration.string, '*'),
                                    ('cron_minute', TemplatedConfiguration.string, '0'),
                                    ('cron_day_of_week', TemplatedConfiguration.string, '*'),
                                    ],
                         }

cfg_file = "{0}/{1}".format(os.path.abspath(os.path.dirname(__file__)), "frontend.ini")
frontend_config = TemplatedConfiguration(cfg_file, template_frontend_config)

# ______________________________________________________________________________ CELERY HELPERS


def _conf_celery(app, broker, backend=None, queue=None):
    app.conf.update(
                     BROKER_URL=broker,
                     CELERY_ACCEPT_CONTENT=['json'],
                     CELERY_TASK_SERIALIZER='json',
                     CELERY_RESULT_SERIALIZER='json'
                     )
    if backend is not None:
        app.conf.update(CELERY_RESULT_BACKEND=backend)

    if queue is not None:
        app.conf.update(
                        CELERY_DEFAULT_QUEUE=queue,
                        # delivery_mode=1 enable transient mode (don't survive to a server restart)
                        CELERY_QUEUES=(
                                       Queue(queue, routing_key=queue),
                                       )
                        )

    app.conf.update(
        CELERYBEAT_SCHEDULE={
            # Database clean
            'clean_db': {
                'task': 'frontend_app.clean_db',
                'schedule': crontab(
                    hour=frontend_config['clean_db']['cron_hour'],
                    minute=frontend_config['clean_db']['cron_minute'],
                    day_of_week=frontend_config['clean_db']['cron_day_of_week']
                ),
                'args': (),
            },
        },
        CELERY_TIMEZONE='UTC'
    )

    return


def conf_brain_celery(app):
    broker = get_brain_broker_uri()
    backend = get_brain_backend_uri()
    queue = frontend_config.broker_brain.queue
    _conf_celery(app, broker, backend, queue)


def conf_frontend_celery(app):
    broker = get_frontend_broker_uri()
    queue = frontend_config.broker_frontend.queue
    _conf_celery(app, broker, queue=queue)


def get_db_uri():
    return "mongodb://%s:%s/" % (frontend_config.mongodb.host, frontend_config.mongodb.port)


def get_brain_celery_timeout():
    return frontend_config.celery_brain.timeout


def get_frontend_celery_timeout():
    return frontend_config.celery_admin.timeout
# ______________________________________________________________________________ BACKEND HELPERS


def _get_backend_uri(backend_config):
    return "redis://%s:%s/%s" % (backend_config.host, backend_config.port, backend_config.db)


def get_brain_backend_uri():
    return _get_backend_uri(frontend_config.backend_brain)

# ______________________________________________________________________________ BROKER HELPERS


def _get_broker_uri(broker_config):
    return "amqp://%s:%s@%s:%s/%s" % (broker_config.username, broker_config.password, broker_config.host, broker_config.port, broker_config.vhost)


def get_brain_broker_uri():
    return _get_broker_uri(frontend_config.broker_brain)


def get_frontend_broker_uri():
    return _get_broker_uri(frontend_config.broker_frontend)
