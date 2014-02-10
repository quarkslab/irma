import sys, os
sys.path.append(os.path.realpath('..'))

from config.dbconfig import MONGODB
from config.config import AMQP_ADDRESS, AMQP_PORT, ADMIN_AMQP_USER, ADMIN_AMQP_PASSWORD, ADMIN_AMQP_VHOST_BROKER, BRAIN_AMQP_USER, BRAIN_AMQP_PASSWORD, BRAIN_AMQP_VHOST_BROKER, PROBE_AMQP_USER, PROBE_AMQP_PASSWORD, PROBE_AMQP_VHOST_BROKER
from config.adminconfig import admin_celery
from config.brainconfig import brain_celery
from config.probeconfig import probe_celery
import pymongo
import amqp
import requests
import libvirt


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

status_ok = 0
status_ko = 1
status_str = [bcolors.OKGREEN + "[+]" + bcolors.ENDC, bcolors.FAIL + "[-]" + bcolors.ENDC]

def print_hdr(msg):
    print
    print bcolors.HEADER + "-> %s <-" % msg + bcolors.ENDC
    print

def print_msg(code_msg_list):
    for (status, line) in code_msg_list:
        print '\t',
        print status_str[status], line

def ping_celery_app(celery):
    try:
        res = []
        ping_status = celery.control.ping(timeout=0.5)

        if len(ping_status) == 0:
            res.append((status_ko, 'celery app %s is down' % celery.main))
        for r in ping_status:
            for host, response in r.items():
                if response['ok'] == u'pong':
                    res.append((status_ok, 'celery app %s is up and running' % host))
                else:
                    res.append((status_ko, 'celery app %s is down' % host))
    except:
        res.append((status_ko, 'no celery running perhaps broker is down on %s' % celery.conf['BROKER_URL']))
    return res

def ping_db(uri):
    try:
        pymongo.Connection(uri)
        return [(status_ok, 'mongodb %s is up and runnning' % uri)]
    except:
        return [(status_ko, 'mongodb %s is down' % uri)]

def ping_rabbitmq(address, port, usr, pwd, vhost):
    try:
        amqp.Connection(host='%s:%s' % (address, port), userid=usr, password=pwd, virtual_host=vhost)
        return [(status_ok, 'rabbitmq vhost %s on %s is up and runnning' % (vhost, address))]
    except:
        return [(status_ko, 'rabbitmq vhost %s on %s is down' % (vhost, address))]

def ping_frontend(url):
    try:
        requests.get(url=url + '/')
        return [(status_ok, 'frontend %s is up and runnning' % url)]
    except:
        return [(status_ko, 'frontend %s is down' % url)]


def ping_libvirt(uri):
    try:
        libvirt.open(uri)
        return [(status_ok, 'libvirt %s is up and runnning' % uri)]
    except:
        return [(status_ko, 'libvirt %s is down' % uri)]
    return

print_hdr("MongoDb")
print_msg(ping_db(MONGODB))

print_hdr("RabbitMQ")
for usr, pwd, vhost in [
                          (ADMIN_AMQP_USER, ADMIN_AMQP_PASSWORD, ADMIN_AMQP_VHOST_BROKER),
                          (BRAIN_AMQP_USER, BRAIN_AMQP_PASSWORD, BRAIN_AMQP_VHOST_BROKER),
                          (PROBE_AMQP_USER, PROBE_AMQP_PASSWORD, PROBE_AMQP_VHOST_BROKER)]:
    print_msg(ping_rabbitmq(AMQP_ADDRESS, AMQP_PORT, usr, pwd, vhost))

print_hdr("Frontend")
print_msg(ping_frontend("http://192.168.130.133:8080"))

print_hdr("Celery")
for app in [admin_celery, brain_celery, probe_celery]:
    print_msg(ping_celery_app(app))
print
