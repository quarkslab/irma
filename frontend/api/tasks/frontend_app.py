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

import logging
import humanfriendly

import celery
from celery.utils.log import get_task_logger

import api.files.services as file_ctrl
import api.scans.services as scan_ctrl
import config.parser as config
from lib.common.utils import humanize_time_str
from lib.irma.common.exceptions import IrmaDatabaseError, IrmaFileSystemError

import api.common.ftp as ftp_ctrl
import api.tasks.braintasks as celery_brain
from api.files_ext.models import FileExt
from api.scans.models import Scan
from lib.irma.common.exceptions import IrmaFtpError
from lib.irma.common.utils import IrmaScanStatus
from api.common.sessions import session_transaction

log = get_task_logger(__name__)

# declare a new application
frontend_app = celery.Celery('frontend_app')
config.conf_frontend_celery(frontend_app)
config.configure_syslog(frontend_app)

# IRMA specific debug messages are enables through
# config file Section: log / Key: debug
if config.debug_enabled():
    def after_setup_logger_handler(sender=None, logger=None, loglevel=None,
                                   logfile=None, format=None,
                                   colorize=None, **kwds):
        config.setup_debug_logger(logging.getLogger(__name__))
        log.debug("debug is enabled")
    celery.signals.after_setup_logger.connect(after_setup_logger_handler)
    celery.signals.after_setup_task_logger.connect(after_setup_logger_handler)


@frontend_app.task(acks_late=True)
def scan_launch(scan_id):
    with session_transaction() as session:
        scan = None
        try:
            log.debug("scan: %s launching", scan_id)
            # Part for common action for whole scan
            scan = Scan.load_from_ext_id(scan_id, session)
            scan_request = scan_ctrl._create_scan_request(
                    scan.files_ext,
                    scan.get_probelist(),
                    scan.mimetype_filtering)
            scan_request = scan_ctrl._add_empty_results(
                    scan.files_ext,
                    scan_request,
                    scan, session)
            # Nothing to do
            if scan_request.nb_files == 0:
                scan.set_status(IrmaScanStatus.finished)
                log.warning("scan %s: finished nothing to do", scan_id)
                return
            # Part for action file_ext by file_ext
            file_ext_id_list = [file.external_id for file in scan.files_ext]
            celery.group(scan_launch_file_ext.si(file_ext_id)
                         for file_ext_id in file_ext_id_list)()
            scan.set_status(IrmaScanStatus.launched)
            session.commit()
            log.info("scan %s: launched", scan_id)
            return
        except Exception as e:
            log.exception(e)
            if scan is not None:
                scan.set_status(IrmaScanStatus.error)


@frontend_app.task(acks_late=True)
def scan_launch_file_ext(file_ext_id):
    file_ext = None
    with session_transaction() as session:
        try:
            file_ext = FileExt.load_from_ext_id(file_ext_id, session)
            scan_id = file_ext.scan.external_id
            log.debug("scan %s: launch scan for file_ext: %s",
                      scan_id, file_ext_id)
            ftp_ctrl.upload_file(file_ext_id, file_ext.file.path)
            # launch new celery scan task on brain
            celery_brain.scan_launch(file_ext_id, file_ext.probes, scan_id)
        except IrmaFtpError as e:
            log.error("file_ext %s: ftp upload error %s", file_ext_id, str(e))
            if file_ext is not None:
                file_ext.scan.set_status(IrmaScanStatus.error_ftp_upload)
        except Exception as e:
            log.exception(e)


@frontend_app.task(acks_late=True)
def scan_result(file_ext_id, probe, result):
    try:
        log.debug("result for file_ext: %s probe: %s",
                  file_ext_id, probe)
        scan_ctrl.handle_output_files(file_ext_id, result)
        scan_ctrl.set_result(file_ext_id, probe, result)
    except IrmaDatabaseError as e:
        log.exception(e)
        raise scan_result.retry(countdown=2, max_retries=3, exc=e)


@frontend_app.task()
def clean_db():
    try:
        cron_cfg = config.frontend_config['cron_clean_file_age']
        max_age_file = cron_cfg['clean_db_file_max_age']
        # 0 means disabled
        if max_age_file == 0:
            log.debug("disabled by config")
            return 0
        # days to seconds
        max_age_file *= 24 * 60 * 60
        nb_files = file_ctrl.remove_files(max_age_file)
        hage_file = humanize_time_str(max_age_file, 'seconds')
        log.info("removed %d files (older than %s)", nb_files, hage_file)
        return nb_files
    except (IrmaDatabaseError, IrmaFileSystemError) as e:
        log.exception(e)
        raise clean_db.retry(countdown=30, max_retries=3, exc=e)


@frontend_app.task()
def clean_fs_size():
    try:
        cron_cfg = config.frontend_config['cron_clean_file_size']
        max_size = cron_cfg['clean_fs_max_size']
        # 0 means disabled
        if max_size == '0':
            log.debug("disabled by config")
            return 0
        max_size_bytes = humanfriendly.parse_size(max_size, binary=True)
        nb_files = file_ctrl.remove_files_size(max_size_bytes)
        log.info("removed %d files", nb_files)
        return nb_files
    except (IrmaDatabaseError, IrmaFileSystemError) as e:
        log.exception(e)
        raise clean_fs_size.retry(countdown=30, max_retries=3, exc=e)

########################
# command line launcher
########################

if __name__ == '__main__':
    options = config.get_celery_options("api.tasks.frontend_app",
                                        "frontend_app")
    frontend_app.worker_main(options)
