import os
from kombu import Queue
from lib.irma.configuration.ini import TemplatedConfiguration

# ______________________________________________________________________________ TEMPLATE

template_frontend_config = {
                         'mongodb': (('host', TemplatedConfiguration.string, None),
                                      ('port', TemplatedConfiguration.integer, 27017),
                                      ('dbname', TemplatedConfiguration.string, None),
                                    ),
                         'collections': (('scan_info', TemplatedConfiguration.string, None),
                                          ('scan_results', TemplatedConfiguration.string, None),
                                          ('scan_files', TemplatedConfiguration.string, None),
                                          ('scan_file_fs', TemplatedConfiguration.string, None),
                                         ),
                         'celery_brain': (('timeout', TemplatedConfiguration.integer, 10),
                                          ),
                         'celery_admin': (('timeout', TemplatedConfiguration.integer, 10),
                                          ),
                         'broker_brain': (
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 5671),
                                    ('vhost', TemplatedConfiguration.string, None),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None),
                                    ('queue' , TemplatedConfiguration.string, None),
                                    ),
                         'broker_admin': (
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 5671),
                                    ('vhost', TemplatedConfiguration.string, None),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None),
                                    ('queue' , TemplatedConfiguration.string, None),
                                    ),
                         'backend_brain': (
                                   ('host', TemplatedConfiguration.string, None),
                                   ('port', TemplatedConfiguration.integer, 6379),
                                   ('db', TemplatedConfiguration.integer, None),
                                   ),
                         'backend_admin': (
                                   ('host', TemplatedConfiguration.string, None),
                                   ('port', TemplatedConfiguration.integer, 6379),
                                   ('db', TemplatedConfiguration.integer, None),
                                   )
                         }


frontend_config = TemplatedConfiguration("frontend.ini", template_frontend_config)

# ______________________________________________________________________________ CELERY HELPERS

def conf_celery(app):
    app.conf.update(
                    CELERY_ACCEPT_CONTENT=['json'],
                    CELERY_TASK_SERIALIZER='json',
                    CELERY_RESULT_SERIALIZER='json'
    )

def conf_celery_queue(app, queue):
    app.conf.update(
                    CELERY_DEFAULT_QUEUE=queue,
                    # delivery_mode=1 enable transient mode (don't survive to a server restart)
                    CELERY_QUEUES=(
                                   Queue(queue, routing_key=queue, delivery_mode=1),
                                   )
                    )

def get_db_uri():
    return "mongodb://%s:%s/" % (frontend_config.mongodb.host, frontend_config.mongodb.port)

def get_brain_celery_timeout():
    return frontend_config.celery_brain.timeout

def get_admin_celery_timeout():
    return frontend_config.celery_admin.timeout
# ______________________________________________________________________________ BACKEND HELPERS

def _get_backend_uri(backend_config):
    return "redis://%s:%s/%s" % (backend_config.host, backend_config.port, backend_config.db)

def get_brain_backend_uri():
    return _get_backend_uri(frontend_config.backend_brain)

def get_admin_backend_uri():
    return _get_backend_uri(frontend_config.backend_admin)

# ______________________________________________________________________________ BROKER HELPERS

def _get_broker_uri(broker_config):
    return  "amqp://%s:%s@%s:%s/%s" % (broker_config.username, broker_config.password, broker_config.host, broker_config.port, broker_config.vhost)

def get_brain_broker_uri():
    return _get_broker_uri(frontend_config.broker_brain)

def get_probe_broker_uri():
    return _get_broker_uri(frontend_config.broker_admin)
