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

from brain.models.sqlobjects import Probe
from brain.helpers.sql import session_query, session_transaction
from lib.irma.common.exceptions import IrmaDatabaseResultNotFound


def register(name, category, mimetype_regexp):
    with session_transaction() as session:
        try:
            probe = Probe.get_by_name(name, session)
            print("probe {0} is already registred "
                  "Updating with new parameters: "
                  "Category:{1} Regexp:{2}".format(name,
                                                   category,
                                                   mimetype_regexp))
            probe.category = category
            probe.mimetype_regexp = mimetype_regexp
            probe.online = True
            probe.update(['category', 'mimetype_regexp', 'online'], session)
        except IrmaDatabaseResultNotFound:
            probe = Probe(name=name,
                          category=category,
                          mimetype_regexp=mimetype_regexp,
                          online=True)
            probe.save(session)
            return


def get_all():
    with session_query() as session:
        probes = Probe.all(session)
        return [p for p in probes if p.online is True]


def get_all_probename():
    probes = get_all()
    probe_list = [p.name for p in probes]
    return probe_list


def all_offline():
    with session_transaction() as session:
        probes = Probe.all(session)
        for p in probes:
            p.online = False
            p.update(['online'], session)
        return


def set_offline(probe_name):
    with session_transaction() as session:
        p = Probe.get_by_name(probe_name, session)
        p.online = False
        p.update(['online'], session)
        return


def set_online(probe_name):
    with session_transaction() as session:
        p = Probe.get_by_name(probe_name, session)
        p.online = True
        p.update(['online'], session)
        return


def get_category(probe_name):
    with session_query() as session:
        p = Probe.get_by_name(probe_name, session)
        return p.category
