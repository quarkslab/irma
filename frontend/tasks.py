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

import celery
import config.parser as config

from celery.utils.log import get_task_logger
from lib.common.utils import humanize_time_str
import frontend.controllers.scanctrl as scan_ctrl
import frontend.controllers.filectrl as file_ctrl
from lib.irma.common.exceptions import IrmaDatabaseError, IrmaFileSystemError


log = get_task_logger(__name__)

# declare a new application
frontend_app = celery.Celery('frontendtasks')
config.conf_frontend_celery(frontend_app)
config.configure_syslog(frontend_app)

# declare a new application
scan_app = celery.Celery('scantasks')
config.conf_brain_celery(scan_app)
config.configure_syslog(scan_app)


@frontend_app.task(acks_late=True)
def scan_launch(scanid):
    try:
        scan_ctrl.launch_asynchronous(scanid)
    except IrmaDatabaseError as e:
        print "Exception has occurred:{0}".format(e)
        raise scan_launch.retry(countdown=2, max_retries=3, exc=e)


@frontend_app.task(acks_late=True)
def scan_launched(scanid):
    try:
        scan_ctrl.set_launched(scanid)
    except IrmaDatabaseError as e:
        print "Exception has occurred:{0}".format(e)
        raise scan_launched.retry(countdown=2, max_retries=3, exc=e)


@frontend_app.task(acks_late=True)
def scan_result(scanid, file_hash, probe, result):
    try:
        scan_ctrl.handle_output_files(scanid, file_hash, probe, result)
        scan_ctrl.set_result(scanid, file_hash, probe, result)
    except IrmaDatabaseError as e:
        print "Exception has occurred:{0}".format(e)
        raise scan_result.retry(countdown=2, max_retries=3, exc=e)


@frontend_app.task()
def clean_db():
    try:
        cron_cfg = config.frontend_config['cron_frontend']
        max_age_file = cron_cfg['clean_db_file_max_age']
        # days to seconds
        max_age_file *= 24 * 60 * 60
        nb_files = file_ctrl.remove_files(max_age_file)
        hage_file = humanize_time_str(max_age_file, 'seconds')
        print("removed {0} files ".format(nb_files) +
              "(older than {0})".format(hage_file))
        return nb_files
    except (IrmaDatabaseError, IrmaFileSystemError) as e:
        print "Exception has occurred:{0}".format(e)
        raise clean_db.retry(countdown=2, max_retries=3, exc=e)
