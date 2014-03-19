import kombu, ssl, tempfile, os

from celery import Celery, current_task
from celery.utils.log import get_task_logger

from config.probe import probe_config as config
from lib.irma.ftp.handler import FtpTls

##############################################################################
# statically import plugins
##############################################################################

from probes.antivirus.antivirus import AntivirusProbe
from probes.antivirus.clam import ClamProbe
from probes.antivirus.comodo_cavl import ComodoCAVLProbe
from probes.antivirus.eset_nod32 import EsetNod32Probe
from probes.antivirus.fprot import FProtProbe
from probes.antivirus.mcafee_vscl import McAfeeVSCLProbe
from probes.antivirus.sophos import SophosProbe
from probes.antivirus.kaspersky import KasperskyProbe
from probes.antivirus.symantec import SymantecProbe

from probes.web.web import WebProbe
from probes.web.virustotal import VirusTotalProbe

from probes.information.information import InformationProbe
from probes.information.analyzer import StaticAnalyzerProbe

from probes.database.database import DatabaseProbe
from probes.database.nsrl import NSRLProbe

##############################################################################
# celery application configuration
##############################################################################

log = get_task_logger(__name__)

# disable insecure serializer (disabled by default from 3.x.x)
if (kombu.VERSION.major) < 3:
    kombu.disable_insecure_serializers()

# build connection strings
broker = "amqp://{user}:{password}@{host}:{port}/{vhost}".format(
    user=config.broker_probe.username, password=config.broker_probe.password,
    host=config.broker_probe.host, port=config.broker_probe.port,
    vhost=config.broker_probe.vhost
)

backend = "redis://{host}:{port}/{database}".format(
    host=config.backend_probe.host, port=config.backend_probe.port,
    database=config.backend_probe.db)

# declare a new application
app = Celery("probe.tasks")
app.conf.update(
    BROKER_URL=broker,
    CELERY_RESULT_BACKEND=backend,
#    CELERY_IGNORE_RESULT=True,
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TASK_SERIALIZER='json',
#    BROKER_USE_SSL = {
#        'ca_certs': config.broker_probe['ssl_ca'],
#        'keyfile': config.broker_probe['ssl_key'],
#        'certfile': config.broker_probe['ssl_cert'],
#        'cert_reqs': ssl.CERT_REQUIRED
#        },
#    BROKER_LOGIN_METHOD='EXTERNAL',
#    CELERY_DISABLE_RATE_LIMITS=True,
#    CELERY_ACKS_LATE=True
)

# determine dynamically queues to connect to
queues = []
probes = sum([ AntivirusProbe.plugins, WebProbe.plugins, DatabaseProbe.plugins, InformationProbe.plugins ], [])
probes = map(lambda pb: pb(conf=config.get(pb.plugin_name, None)), probes)
probes = filter(lambda pb: pb.ready(), probes)
probes = dict((type(pb).plugin_name, pb) for pb in probes)
for probe in probes.keys():
    queues.append(kombu.Queue(probe, routing_key=probe))

# update configuration
app.conf.update(
    CELERY_QUEUES=tuple(queues),
)

##############################################################################
# declare celery tasks
##############################################################################

@app.task()
def probe_scan(frontend, scanid, filename):
    try:
        # retrieve queue name and the associated plugin
        routing_key = current_task.request.delivery_info['routing_key']
        probe = probes[routing_key]
        conf_ftp = config.ftp_brain
        (fd, tmpname) = tempfile.mkstemp()
        os.close(fd)
        with FtpTls(conf_ftp.host, conf_ftp.port, conf_ftp.username, conf_ftp.password) as ftps:
            ftps.download("{0}/{1}".format(frontend, scanid), filename, tmpname)
        results = probe.run(tmpname)
        # Some AV always delete suspicious file
        if os.path.exists(tmpname):
            os.remove(tmpname)
        return results
    except Exception as e:
        log.exception("Exception has occured: {0}".format(e))
        raise probe_scan.retry(countdown=30, max_retries=5)

##############################################################################
# command line launcher, only for debug purposes
##############################################################################

if __name__ == '__main__':
    app.worker_main([
        '--app=probe.tasks:app',    # app instance to use
        '-l', 'info',               # logging level
        '--without-gossip',         # do not subscribe to other workers events.
        '--without-mingle',         # do not synchronize with other workers at startup
        '--without-heartbeat',      # do not send event heartbeats
    ])
