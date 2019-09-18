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
import ntpath

from sqlalchemy import Column, Integer, ForeignKey, String, \
    UniqueConstraint, and_, inspect
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import relationship, backref, with_polymorphic
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql import func

from api.common.models import Base, tables_prefix
from api.files.models import File
from api.scans.models import Scan
from api.tags.models import Tag
from irma.common.utils.utils import UUID
from irma.common.utils.compat import timestamp
from irma.common.base.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError
from irma.common.base.utils import IrmaProbeType


log = logging.getLogger(__name__)


class FileExt(Base):
    submitter_type = "unknown"
    __tablename__ = '{0}fileExt'.format(tables_prefix)
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
    # Many to one FileExt <-> File
    id_file = Column(
        Integer,
        ForeignKey('{0}file.id'.format(tables_prefix)),
        nullable=False,
        index=True,
    )
    file = relationship(
        File,
        backref=backref('files_ext'),
        foreign_keys='FileExt.id_file'
    )
    name = Column(
        String(length=255),
        nullable=True,
        name='name'
    )
    # Many to one FileExt <-> Scan
    id_scan = Column(
        Integer,
        ForeignKey('{0}scan.id'.format(tables_prefix)),
        index=True,
    )
    scan = relationship(
        "Scan",
        backref=backref('files_ext')
    )
    # Many to one FileExt <-> File
    id_parent = Column(
        Integer,
        ForeignKey('{0}file.id'.format(tables_prefix)),
    )
    parent = relationship(File,
                          backref="children",
                          foreign_keys='FileExt.id_parent')
    depth = Column(
        Integer,
        name='depth')

    submitter = Column(
        String(50),
        name="submitter")
    __mapper_args__ = {
        'polymorphic_on': submitter,
        'polymorphic_identity': submitter_type
    }

    # insure there are no dup external_id
    __table_args__ = (UniqueConstraint('external_id'),)

    def __init__(self, file, name, depth=0):
        self.external_id = UUID.generate()
        self.file = file
        self.name = name
        self.depth = depth

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
            filext_plus_cls = with_polymorphic(FileExt, [cls])
            return session.query(filext_plus_cls).filter(
                    cls.external_id == str(external_id)
            ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)

    @property
    def probes(self):
        return [x.name for x in self.probe_results]

    @property
    def probes_total(self):
        return len(self.probe_results)

    @property
    def probes_finished(self):
        return sum(1 for pr in self.probe_results if pr.status is not None)

    @property
    def status(self):
        if not self.probe_results \
                or any(pr.status is None for pr in self.probe_results):
            return None
        else:
            return 1 if any(pr.type == IrmaProbeType.antivirus
                            and pr.status == 1
                            for pr in self.probe_results) else 0

    def get_probe_results(self, formatted=True, results_as="dict"):
        if results_as == "dict":
            results = {}
        elif results_as == "list":
            results = []
        else:
            raise ValueError("unknown output format")

        for pr in self.probe_results:
            if pr.status is None:
                continue
            result = pr.get_details(formatted)
            if results_as == "dict":
                type = result.pop('type')
                name = result.pop('name')
                if type not in results:
                    results[type] = {}
                results[type].update({name: result})
            else:
                results.append(result)
        return results

    @classmethod
    def query_find_by_name(cls, name, tags, session):
        last_ids = session.query(cls.id_file,
                                 cls.name,
                                 func.max(cls.id).label('last_id')) \
            .group_by(cls.id_file, cls.name).subquery()

        query = session.query(cls) \
            .join((last_ids, and_(cls.id_file == last_ids.c.id_file,
                                  cls.name == last_ids.c.name,
                                  cls.id == last_ids.c.last_id))) \
            .join(File, File.id == cls.id_file) \
            .filter(cls.name.like("%{0}%".format(name))) \
            .order_by(cls.name)

        # Update the query with tags if user asked for it
        if tags is not None:
            query = query.join(File.tags)
            for tagid in tags:
                # check if tag exists
                session.query(Tag).filter_by(id=tagid).one()
                query = query.filter(File.tags.any(Tag.id == tagid))

        return query

    @classmethod
    def query_find_by_hash(cls, hash_type, hash_value, tags, session,
                           distinct_name=True):
        if distinct_name:
            last_ids = session.query(cls.id_file,
                                     cls.name,
                                     func.max(cls.id).label('last_id')) \
                .group_by(cls.id_file, cls.name).subquery()

            query = session.query(cls) \
                .join((last_ids, and_(cls.id_file == last_ids.c.id_file,
                                      cls.name == last_ids.c.name,
                                      cls.id == last_ids.c.last_id)))
        else:
            query = session.query(cls)

        query = query.join(File, File.id == cls.id_file)

        query = query.filter(getattr(File, hash_type) == hash_value) \
            .order_by(cls.name)
        # Update the query with tags if user asked for it
        if tags is not None:
            query = query.join(File.tags)
            for tagid in tags:
                # check if tag exists
                session.query(Tag).filter_by(id=tagid).one()
                query = query.filter(File.tags.any(Tag.id == tagid))

        return query

    def fetch_probe_result(self, probe):
        pr_list = [x for x in self.probe_results if x.name == probe]
        if len(pr_list) > 1:
            raise IrmaDatabaseError("Integrity error: multiple results for "
                                    "file {0} probe {1}".format(self.name,
                                                                probe))
        elif len(pr_list) == 0:
            raise IrmaDatabaseError("No result created for "
                                    "file {0} probe {1}".format(self.name,
                                                                probe))
        return pr_list[0]

    def set_result(self, probe, result):
        # Update file last_scan timestamp
        self.file.timestamp_last_scan = timestamp()
        # Retrieve empty probe result
        pr = self.fetch_probe_result(probe)
        # Update main reference results with fresh results
        pr.file = self.file
        # fill ProbeResult with probe raw results
        pr.doc = result
        pr.status = result.get('status', None)
        s_type = result.get('type', None)
        pr.type = IrmaProbeType.normalize(s_type)

    @property
    def other_results(self):
        session = inspect(self).session
        query = session.query(FileExt).join(Scan).filter(
            FileExt.id_file == self.id_file).order_by(Scan.date)
        return query.all()

    def hook_finished(self):
        """Function called when scan is finished
        """
        results = self.get_probe_results(results_as="list")
        submitter_id = getattr(self, 'submitter_id', 'undefined')
        log.info("[files_results] date: %s file_id: %s scan_id: %s "
                 "status: %s probes: %s submitter: %s submitter_id: %s",
                 self.scan.date, self.external_id,
                 self.scan.external_id, "Infected" if self.status else "Clean",
                 ', '.join(self.probes), self.submitter,
                 submitter_id)
        for result in results:
            if result.duration is None:
                duration = 0
            else:
                duration = result.duration
            if result.type == "antivirus":
                log.info('[av_results] date: %s av_name: "%s" '
                         "status: %d "
                         "virus_name: \"%s\" file_id: %s "
                         "file_sha256: %s "
                         "scan_id: %s "
                         "duration: %f submitter: %s submitter_id: %s",
                         self.scan.date, result.name, result.status,
                         result.results,
                         self.external_id,
                         self.file.sha256, self.scan.external_id, duration,
                         self.submitter, submitter_id)
            else:
                log.info('[probe_results] date: %s name: "%s" '
                         "status: %d file_sha256: %s "
                         "file_id: %s "
                         "duration: %f "
                         "submitter: %s "
                         "submitter_id: %s",
                         self.scan.date, result.name, result.status,
                         self.external_id, self.file.sha256,
                         duration,
                         self.submitter,
                         submitter_id)


class FileWeb(FileExt):
    submitter_type = "webui"
    __tablename__ = '{0}fileWeb'.format(tables_prefix)
    __mapper_args__ = {'polymorphic_identity': submitter_type}
    # Fields
    id = Column(
        Integer,
        ForeignKey('{0}fileExt.id'.format(tables_prefix)),
        name='id',
        primary_key=True
    )


class FileProbeResult(FileExt):
    submitter_type = "probe_result"
    __tablename__ = '{0}fileProbeResult'.format(tables_prefix)
    __mapper_args__ = {'polymorphic_identity': submitter_type}
    # Fields
    id = Column(
        Integer,
        ForeignKey('{0}fileExt.id'.format(tables_prefix)),
        name='id',
        primary_key=True
    )
    id_probe_parent = Column(
        Integer,
        ForeignKey('{0}probeResult.id'.format(tables_prefix)),
        nullable=False
    )
    # Many to one FileProbe <-> ProbeResult
    probe_result_parent = relationship(
        "ProbeResult",
        backref='files_ext_generated',
        foreign_keys='FileProbeResult.id_probe_parent'
    )

    def __init__(self, file, filename, probe_result_parent, depth):
        super(FileProbeResult, self).__init__(file, filename)
        self.probe_result_parent = probe_result_parent
        self.depth = depth


class FileCli(FileExt):
    submitter_type = "cli"
    __tablename__ = '{0}fileCli'.format(tables_prefix)
    __mapper_args__ = {'polymorphic_identity': submitter_type}
    # Fields
    id = Column(
        Integer,
        ForeignKey('{0}fileExt.id'.format(tables_prefix)),
        name='id',
        primary_key=True
    )
    path = Column(
        String(length=255),
        nullable=True,
        name='path'
    )

    def __init__(self, file, filepath):
        (path, name) = ntpath.split(filepath)
        super(FileCli, self).__init__(file, name)
        self.path = path


class FileKiosk(FileExt):
    submitter_type = "kiosk"
    __tablename__ = '{0}fileKiosk'.format(tables_prefix)
    __mapper_args__ = {'polymorphic_identity': submitter_type}
    # Fields
    id = Column(
        Integer,
        ForeignKey('{0}fileExt.id'.format(tables_prefix)),
        name='id',
        primary_key=True
    )
    path = Column(
        String(length=255),
        nullable=True,
        name='path'
    )
    submitter_id = Column(
        String(length=255),
        nullable=True,
        name='submitter_id'
        )

    def __init__(self, file, filepath, payload):
        (path, name) = ntpath.split(filepath)
        super(FileKiosk, self).__init__(file, name)
        self.path = path
        self.submitter_id = payload.pop('submitter_id', None)


class FileSuricata(FileExt):
    submitter_type = "suricata"
    __tablename__ = '{0}fileSuricata'.format(tables_prefix)
    __mapper_args__ = {'polymorphic_identity': submitter_type}
    # Fields
    id = Column(
        Integer,
        ForeignKey('{0}fileExt.id'.format(tables_prefix)),
        name='id',
        primary_key=True
    )
    context = Column(
        JSONB,
        name='context'
    )

    def __init__(self, file, filename, context):
        super(FileSuricata, self).__init__(file, filename)
        self.context = context
