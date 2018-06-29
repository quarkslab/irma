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

from sqlalchemy import Column, Integer, Numeric, Boolean,\
    ForeignKey, String, select, func
from sqlalchemy.orm import relationship, backref, subqueryload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.hybrid import hybrid_property

from irma.common.base.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError, IrmaCoreError
from irma.common.utils import compat
from irma.common.base.utils import IrmaScanStatus
from irma.common.utils.utils import UUID
from api.common.models import Base, tables_prefix

import api.probes.services as probe_ctrl

import logging


log = logging.getLogger(__name__)


class Scan(Base):
    __tablename__ = '{0}scan'.format(tables_prefix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    external_id = Column(
        String(length=36),
        index=True,
        nullable=False,
        name='external_id'
    )
    date = Column(
        Integer,
        nullable=False,
        name='date'
    )
    ip = Column(
        String,
        name='ip'
    )
    probelist = Column(
        String,
        name='probelist'
    )
    force = Column(
        Boolean,
        name='force'
    )
    mimetype_filtering = Column(
        Boolean,
        name='mimetype_filtering'
    )
    resubmit_files = Column(
        Boolean,
        name='resubmit_files'
    )

    def get_probelist(self):
        return self.probelist.split(",")

    def set_probelist(self, value):
        self.probelist = ",".join(value)

    def __init__(self, date, ip, force=True, mimetype_filtering=True,
                 resubmit_files=True, files_ext=[], probes=None):
        super(Scan, self).__init__()
        self.external_id = UUID.generate()
        self.date = date
        self.ip = ip
        self.force = force
        self.mimetype_filtering = mimetype_filtering
        self.resubmit_files = resubmit_files

        self.set_status(IrmaScanStatus.empty)

        if files_ext:
            for fe in files_ext:
                log.info("scan {} adding file {}"
                         .format(self.external_id, fe.external_id))
                fe.scan = self
            self.set_status(IrmaScanStatus.ready)

        self.set_probelist(probe_ctrl.check_probe(probes))

        log.debug("scan {}: created".format(self.external_id))
        log.debug("scan {}: Force {} MimeF {} Resub {} Probes {}"
                  .format(self.external_id, self.force,
                          self.mimetype_filtering, self.resubmit_files,
                          probes))

    @classmethod
    def query_joined(cls, session):
        """Returns a query with sub-objects loaded
        by default and not on access.
        SQL Relations:
        Scan 1 - N FileExt N - N ProbeResult
        :param session: SQL session
        :return: session query for Scan
        """
        return session.query(cls).options(
                    subqueryload("files_ext").
                    subqueryload("probe_results"))

    @classmethod
    def load_from_ext_id(cls, external_id, session):
        """Find the object in the database
        :param external_id: the id to look for
        :param session: the session to use
        :rtype: cls
        :return: the object that corresponds to the external_id
        :raise: IrmaDatabaseResultNotFound, IrmaDatabaseError
        """
        try:
            query = cls.query_joined(session)
            return query.filter(
                cls.external_id == str(external_id)
            ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)

    def finished(self):
        """Tell if the scan is over or not
        :rtype: boolean
        :return: True if the scan is over
        """
        if self.status == IrmaScanStatus.finished:
            return True
        # Check min. status
        # It could happend that launched status
        # is not yet received and files_ext are already
        # there so just check that we are at least at uploaded
        if self.status < IrmaScanStatus.uploaded:
            return False
        return all(fe.status is not None for fe in self.files_ext)

    @hybrid_property
    def status(self):
        return max(evt.status for evt in self.events)

    @status.expression
    def status(cls):
        query = select([func.max(ScanEvents.status)])
        query = query.where(cls.id == ScanEvents.id_scan)
        return query.as_scalar()

    @property
    def probes_total(self):
        total = 0
        for file_ext in self.files_ext:
            total += file_ext.probes_total
        return total

    @property
    def probes_finished(self):
        finished = 0
        for file_ext in self.files_ext:
            finished += file_ext.probes_finished
        return finished

    @property
    def files(self):
        return list(set([file_ext.file for file_ext in self.files_ext]))

    def set_status(self, status_code):
        if status_code not in IrmaScanStatus.label.keys():
            raise IrmaCoreError("Trying to update with an unknown status")
        if status_code not in [evt.status for evt in self.events]:
            evt = ScanEvents(status_code, self)
            self.events.append(evt)


class ScanEvents(Base):
    __tablename__ = '{0}scanEvents'.format(tables_prefix)

    # Fields
    id = Column(
            Integer,
            autoincrement=True,
            nullable=False,
            primary_key=True,
            name='id'
    )
    status = Column(
            Integer,
            nullable=False,
            name='status'
    )
    timestamp = Column(
            Numeric(asdecimal=False),
            nullable=False,
            name='timestamp'
    )
    # Many to one ScanEvents <-> Scan
    id_scan = Column(
            Integer,
            ForeignKey('{0}scan.id'.format(tables_prefix)),
            index=True,
            nullable=False
    )
    scan = relationship(
            "Scan",
            backref=backref('events')
    )

    def __init__(self, status, scan):
        super(ScanEvents, self).__init__()
        self.status = status
        self.timestamp = compat.timestamp()
        self.scan = scan
