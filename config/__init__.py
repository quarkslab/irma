import os
from kombu import Queue
from lib.irma.configuration.ini import TemplatedConfiguration

# ______________________________________________________________________________ TEMPLATE

template_probe_config = {
                         'probe': [('avname', TemplatedConfiguration.string, None), ],
                         'broker_probe': [
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 5672),
                                    ('vhost', TemplatedConfiguration.string, None),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None)
                                    ],
                         'backend_probe': [
                                   ('host', TemplatedConfiguration.string, None),
                                   ('port', TemplatedConfiguration.integer, 6379),
                                   ('db', TemplatedConfiguration.integer, None),
                                   ],
                         'ftp_brain': [
                                    ('host', TemplatedConfiguration.string, None),
                                    ('port', TemplatedConfiguration.integer, 21),
                                    ('username', TemplatedConfiguration.string, None),
                                    ('password' , TemplatedConfiguration.string, None),
                                    ],
                         }


probe_config = TemplatedConfiguration("probe.ini", template_probe_config)

# ______________________________________________________________________________ CELERY HELPERS


# ______________________________________________________________________________ CELERY HELPERS

def _conf_celery(app, broker, backend, queue=None):
    app.conf.update(
                     BROKER_URL=broker,
                     CELERY_RESULT_BACKEND=backend,
                     CELERY_ACCEPT_CONTENT=['json'],
                     CELERY_TASK_SERIALIZER='json',
                     CELERY_RESULT_SERIALIZER='json'
                     )
    if queue is not None:
        app.conf.update(
                        CELERY_DEFAULT_QUEUE=queue,
                        # delivery_mode=1 enable transient mode (don't survive to a server restart)
                        CELERY_QUEUES=(
                                       Queue(queue, routing_key=queue),
                                       )
                        )
    return

def conf_probe_celery(app):
    broker = get_probe_broker_uri()
    backend = get_probe_backend_uri()
    # Each probe is connected to the queue with the probe name
    queue = probe_config.probe.avname
    _conf_celery(app, broker, backend, queue)

# ______________________________________________________________________________ BACKEND HELPERS

def _get_backend_uri(backend_config):
    return "redis://%s:%s/%s" % (backend_config.host, backend_config.port, backend_config.db)

def get_probe_backend_uri():
    return _get_backend_uri(probe_config.backend_probe)

# ______________________________________________________________________________ BROKER HELPERS

def _get_broker_uri(broker_config):
    return  "amqp://%s:%s@%s:%s/%s" % (broker_config.username, broker_config.password, broker_config.host, broker_config.port, broker_config.vhost)

def get_probe_broker_uri():
    return _get_broker_uri(probe_config.broker_probe)
