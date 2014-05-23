#
# Copyright (c) 2014 QuarksLab.
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

import random
from bson import ObjectId
from hashlib import sha256


# =====================
#  Frontend Exceptions
# =====================

class IrmaFrontendWarning(Exception):
    pass


class IrmaFrontendError(Exception):
    pass


# =============================
#  Frontend response formatter
# =============================

class IrmaFrontendReturn:
    @staticmethod
    def response(code, msg, **kwargs):
        ret = {'code': code, 'msg': msg}
        ret.update(kwargs)
        return ret

    @staticmethod
    def success(**kwargs):
        code = IrmaReturnCode.success
        msg = "success"
        return IrmaFrontendReturn.response(code, msg, **kwargs)

    @staticmethod
    def warning(msg, **kwargs):
        code = IrmaReturnCode.warning
        return IrmaFrontendReturn.response(code, msg, **kwargs)

    @staticmethod
    def error(msg, **kwargs):
        code = IrmaReturnCode.error
        return IrmaFrontendReturn.response(code, msg, **kwargs)


# =============
#  Return code
# =============

class IrmaReturnCode:
    success = 0
    warning = 1
    error = -1
    label = {success: "success", warning: "warning", error: "error"}


class IrmaScanStatus:
    created = 0
    launched = 10
    cancelling = 20
    cancelled = 21
    processed = 30
    finished = 50
    flushed = 100
    label = {
        created: "created",
        launched: "launched",
        cancelling: "being cancelled",
        cancelled: "cancelled",
        processed: "processed",
        finished: "finished",
        flushed: "flushed"
    }


# ====================
#  Irma system mockup
# ====================

session = {}
total = {}
progress = {}
probes = ["nsrl", "symantec", "virustotal", "sophos",
          "clamav", "kaspersky", "mcafee"]
results_filename = {
    "eicar.com": {
        u'nsrl': {
            u'result': [u'eicar.com.txt,68,18115,358,']},
        u'clamav': {
            u'version': u'ClamAV 0.97.8/18517/Wed Feb 26 10:44:17 2014',
            u'result': u'Eicar-Test-Signature'},
        u'virustotal': {
            u'result': u'48/50 positives'},
        u'kaspersky': {
            u'version': u'Kaspersky Anti-Virus (R) 14.0.0.4837',
            u'result': u'EICAR-Test-File'}
        }
    }

results = [
    # Random File 1
    {"nsrl": {
        "result": "Not found"},
     "symantec": {
         "version": "null",
         "result": "clean"},
     "virustotal": {
         "result": "41/48 positives"},
     "sophos": {
         "version": "Product version           : 1.01.1\n\
           Engine version            : 3.50.1\n\
           Virus data version        : 4.97G\n\
           User interface version    : 2.91.000\n\
           Platform                  : Win32/Intel\n\
           Released                  : 15 January 2014\n\
           Total viruses (with IDEs) : 6304167",
         "result": "Mal/Inject-CEE"},
     "clamav": {
         "version": "ClamAV 0.97.8/18444/Thu Feb  6 09:07:44 2014",
         "result": "Win.Trojan.Agent-168190"},
     "kaspersky": {
         "version": "Kaspersky Anti-Virus (R) 14.0.0.4837",
         "result": "HEUR:Trojan.Win32.Generic"},
     "mcafee": {
         "version": "McAfee VirusScan Command Line for Win32 \
         Version: 6.0.1.318\n\
           AV Engine version: 5400.1158 for Win32.\n\
           Dat set version: 7337 created Feb 2 2014\n\
           Scanning for 668917 viruses, trojans and variants.\n",
         "result": "clean"}
     },
    # Random File 2
    {"clamav": {
        "version": "ClamAV 0.97.8/18443/Thu Feb  6 03:06:35 2014",
        "result": "Win.Trojan.Viking-49"},
     "sophos": {
         "version": "Product version           : 1.01.1\n\
            Engine version            : 3.50.1\n\
            Virus data version        : 4.97G\n\
            User interface version    : 2.91.000\n\
            Platform                  : Win32/Intel\n\
            Released                  : 15 January 2014\n\
            Total viruses (with IDEs) : 6304167",
         "result": "W32/Jadtre-C"},
     "nsrl": {
         "result": "Not found"},
     "symantec": {
         "version": "null",
         "result": "clean"},
     "virustotal": {
         "result": "40/46 positives"}
     },
    # Random File 3
    {"sophos": {
        "version": "Product version           : 1.01.1\n\
            Engine version            : 3.50.1\n\
            Virus data version        : 4.97G\n\
            User interface version    : 2.91.000\n\
            Platform                  : Win32/Intel\n\
            Released                  : 15 January 2014\n\
            Total viruses (with IDEs) : 6304167",
        "result": "clean"},
     "nsrl": {
         "result": "Not found"},
     "clamav": {
         "version": "ClamAV 0.97.8/18443/Thu Feb  6 03:06:35 2014",
         "result": "clean"},
     "virustotal": {"result": "28/47 positives"}
     },
    # Random File 4
    {"nsrl": {
        "result": "Not found"},
        "symantec": {
            "version": "null",
            "result": "clean"},
        "virustotal": {
            "result": "24/46 positives"},
        "sophos": {
            "version": "Product version           : 1.01.1\n\
            Engine version            : 3.50.1\n\
            Virus data version        : 4.97G\n\
            User interface version    : 2.91.000\n\
            Platform                  : Win32/Intel\n\
            Released                  : 15 January 2014\n\
            Total viruses (with IDEs) : 6304167",
            "result": "Mal/SillyFDC-AH"},
        "clamav": {
            "version": "ClamAV 0.97.8/18420/Fri Jan 31 15:01:15 2014",
            "result": "clean"},
        "kaspersky": {
            "version": "Kaspersky Anti-Virus (R) 14.0.0.4837",
            "result": "Worm.Win32.Vobfus.ehvc"},
        "mcafee": {
            "version": "McAfee VirusScan Command Line for \
            Win32 Version: 6.0.1.318\n\
            AV Engine version: 5400.1158 for Win32.\n\
            Dat set version: 7337 created Feb 2 2014\n\
            Scanning for 668917 viruses, trojans and variants.\n",
            "result": "W32/Autorun.worm.aaeh virus"}
     },
    # Random File 5
    {"sophos": {
        "version": "Product version           : 1.01.1\n\
            Engine version            : 3.50.1\n\
            Virus data version        : 4.97G\n\
            User interface version    : 2.91.000\n\
            Platform                  : Win32/Intel\n\
            Released                  : 15 January 2014\n\
            Total viruses (with IDEs) : 6304167",
        "result": "W32/SillyFDC-KP"},
        "nsrl": {
            "result": "Not found"},
        "clamav": {
            "version": "ClamAV 0.97.8/18443/Thu Feb  6 03:06:35 2014",
            "result": "clean"},
        "virustotal": {
            "result": "30/46 positives"}
     },
    # Random File 6
    {"nsrl": {
        "result": "Not found"},
        "symantec": {
            "version": "null",
            "result": "clean"},
        "virustotal": {
            "result": "41/47 positives"},
        "sophos": {
            "version": "Product version           : 1.01.1\n\
            Engine version            : 3.50.1\n\
            Virus data version        : 4.97G\n\
            User interface version    : 2.91.000\n\
            Platform                  : Win32/Intel\n\
            Released                  : 15 January 2014\n\
            Total viruses (with IDEs) : 6304167",
            "result": "W32/Gamarue-BK"},
        "clamav": {
            "version": "ClamAV 0.97.8/18444/Thu Feb  6 09:07:44 2014",
            "result": "clean"},
        "mcafee": {
            "version": "McAfee VirusScan Command Line for \
            Win32 Version: 6.0.1.318\n\
            AV Engine version: 5400.1158 for Win32.\n\
            Dat set version: 7337 created Feb 2 2014\n\
            Scanning for 668917 viruses, trojans and variants.\n",
            "result": "W32/Worm-FKU!37C88D1EA50D virus"}}]


def scan_new():
    """ Create new scan

    :rtype: str
    :return: scan id
    """
    global session, total, progress
    scanid = str(ObjectId())
    session[scanid] = {}
    session[scanid]['files'] = {}
    total[scanid] = 0
    progress[scanid] = 0
    return scanid


def scan_add(scanid, files):
    """ add file(s) to the specified scan

    :param scanid: id returned by scan_new
    :param files: dict of 'filename':str, 'data':str
    :rtype: int
    :return: int - total number of files for the scan
    """
    global session, total
    if scanid not in session:
        raise IrmaFrontendError("Unknown scanid")
    for (name, data) in files.items():
        hashval = sha256(data).hexdigest()
        print 'Name', name
        if name in results_filename:
            session[scanid]['files'].update(
                {hashval: {
                    'filename': name,
                    'results': results_filename[name]}})
        else:
            rand = random.randrange(len(results))
            session[scanid]['files'].update(
                {hashval: {
                    'filename': name,
                    'results': results[rand]}})
        print "Result", session[scanid]['files']
        total[scanid] += 1
    return total[scanid]


def scan_launch(scanid, _, probelist):
    """ launch specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'code': int, 'msg': str [, optional 'probe_list':list]
    :return:
        on success 'probe_list' is the list of probes used for the scan
        on error 'msg' gives reason message
    :raise: IrmaDataBaseError, IrmaFrontendError
    """
    global session
    if scanid not in session:
        raise IrmaFrontendError("Unknown scanid")
    if probelist is None:
        probelist = probes
    session[scanid]['probelist'] = probelist
    return probelist


def scan_results(scanid):
    """ get all results from files of specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of sha256 value: dict of ['filename':str,
        'results':dict of [str probename: dict [results of probe]]]
    :return:
        dict of results for each hash value
    """
    if scanid not in session:
        raise IrmaFrontendError("Unknown scanid")
    res = {}
    probelist = session[scanid]['probelist']
    for (hashval, info) in session[scanid]['files'].items():
        res[hashval] = {}
        res[hashval]['filename'] = info['filename']
        for k, v in info['results'].items():
            if k in probelist:
                res[hashval]['results'][k] = v
    return res


def scan_progress(scanid):
    """ get scan progress for specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of 'total':int, 'finished':int, 'successful':int
    :return:
        dict with total/finished/succesful jobs submitted by irma-brain
    :raise: IrmaFrontendWarning, IrmaFrontendError
    """
    global progress
    if scanid not in session:
        raise IrmaFrontendError("Unknown scanid")
    if progress[scanid] == total[scanid]:
        reason = IrmaScanStatus.label[IrmaScanStatus.finished]
        raise IrmaFrontendWarning(reason)
    else:
        # simulate a progression of one job each progress request
        progress[scanid] += 1
    if progress[scanid] == total[scanid]:
        reason = IrmaScanStatus.label[IrmaScanStatus.processed]
        raise IrmaFrontendWarning(reason)
    else:
        res = {}
        res['finished'] = progress[scanid]
        res['total'] = total[scanid]
        res['successful'] = progress[scanid]
        return res


def scan_cancel(scanid):
    """ cancel all remaining jobs for specified scan

    :param scanid: id returned by scan_new
    :rtype: dict of \
        'cancel_details': total':int, 'finished':int, 'cancelled':int
    :return:
        informations about number of cancelled jobs by irma-brain
    :raise: IrmaFrontendWarning, IrmaFrontendError
    """
    global progress
    if scanid not in session:
        raise IrmaFrontendError("Unknown scanid")
    if progress[scanid] == total[scanid]:
        reason = IrmaScanStatus.label[IrmaScanStatus.finished]
        raise IrmaFrontendWarning(reason)
    nb_cancelled = total[scanid] - progress[scanid]
    progress[scanid] = total[scanid]
    res = {}
    res['finished'] = progress[scanid]
    res['total'] = total[scanid]
    res['cancelled'] = nb_cancelled
    return res


def probe_list():
    """ get active probe list

    :rtype: list of str
    :return:
        list of probes names
    """
    return probes
