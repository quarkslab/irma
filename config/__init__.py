import os
from kombu import Queue
from lib.irma.configuration.ini import TemplatedConfiguration

# ______________________________________________________________________________ TEMPLATE

template_brain_config = {
                         'mongodb': (('host', TemplatedConfiguration.string, None),
                                      ('port', TemplatedConfiguration.integer, 27017),
                                      ('dbname', TemplatedConfiguration.string, None)
                                    ),
                         'collections': (('scan_info', TemplatedConfiguration.string, None),
                                          ('scan_results', TemplatedConfiguration.string, None),
                                          ('scan_files', TemplatedConfiguration.string, None),
                                          ('scan_file_fs', TemplatedConfiguration.string, None)
                                         ),
                         'broker_brain': (
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 5671),
                                    ('vhost', TemplatedConfiguration.string, None),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None),
                                    ('queue' , TemplatedConfiguration.string, None)
                                    ),
                         'broker_probe': (
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 5671),
                                    ('vhost', TemplatedConfiguration.string, None),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None)
                                    ),
                         'backend_brain': (
                                   ('host', TemplatedConfiguration.string, None),
                                   ('port', TemplatedConfiguration.integer, 6379),
                                   ('db', TemplatedConfiguration.integer, None),
                                   ),
                         'backend_probe': (
                                   ('host', TemplatedConfiguration.string, None),
                                   ('port', TemplatedConfiguration.integer, 6379),
                                   ('db', TemplatedConfiguration.integer, None),
                                   )
                         }


brain_config = TemplatedConfiguration("brain.ini", template_brain_config)

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

# ______________________________________________________________________________ BACKEND HELPERS

def _get_backend_uri(backend_config):
    return "redis://%s:%s/%s" % (backend_config.host, backend_config.port, backend_config.db)

def get_brain_backend_uri():
    return _get_backend_uri(brain_config.backend_brain)

def get_probe_backend_uri():
    return _get_backend_uri(brain_config.backend_probe)

# ______________________________________________________________________________ BROKER HELPERS

def _get_broker_uri(broker_config):
    return  "amqp://%s:%s@%s:%s/%s" % (broker_config.username, broker_config.password, broker_config.host, broker_config.port, broker_config.vhost)

def get_brain_broker_uri():
    return _get_broker_uri(brain_config.broker_brain)

def get_probe_broker_uri():
    return _get_broker_uri(brain_config.broker_probe)
