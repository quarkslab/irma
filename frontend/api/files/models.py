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

import os
import logging

from sqlalchemy import Column, BigInteger, Integer, Numeric, String, \
    UniqueConstraint, inspect, desc, func, Index

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from irma.common.base.exceptions import IrmaDatabaseResultNotFound, \
    IrmaDatabaseError, IrmaFileSystemError
from irma.common.utils import compat
from irma.common.utils.hash import sha256sum, sha1sum, md5sum
from irma.common.utils.mimetypes import Magic
from irma.common.utils.utils import save_to_file

from api.common.utils import build_sha256_path
from api.common.models import Base, tables_prefix
from api.tags.models import Tag
from api.probe_results.models import ProbeResult


log = logging.getLogger(__name__)


class File(Base):
    __tablename__ = '{0}file'.format(tables_prefix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    sha256 = Column(
        String(length=64),
        index=True,
        name='sha256'
    )
    sha1 = Column(
        String(length=40),
        index=True,
        name='sha1'
    )
    md5 = Column(
        String(length=32),
        index=True,
        name='md5'
    )
    timestamp_first_scan = Column(
        Numeric(asdecimal=False),
        nullable=False,
        name='timestamp_first_scan'
    )
    timestamp_last_scan = Column(
        Numeric(asdecimal=False),
        nullable=False,
        name='timestamp_last_scan'
    )
    size = Column(
        BigInteger,
        name='size',
        nullable=False
    )
    mimetype = Column(
        String,
        name='mimetype'
    )
    path = Column(
        String(length=255),
        name='path'
    )
    __table_args__ = (UniqueConstraint('sha256', name='u_file_sha256'),
                      Index('ix_irma_file_ts_pathnotnull',
                            'timestamp_last_scan',
                            postgresql_where=(path != None))  # noqa
                      )

    def __init__(self, sha256, sha1, md5, size, mimetype, path,
                 timestamp_first_scan, timestamp_last_scan, tags=None):
        super(File, self).__init__()

        self.sha256 = sha256
        self.sha1 = sha1
        self.md5 = md5
        self.size = size
        self.mimetype = mimetype
        self.path = path
        self.timestamp_first_scan = timestamp_first_scan
        self.timestamp_last_scan = timestamp_last_scan
        if tags is None:
            self.tags = []
        else:
            self.tags = tags

    def add_tag(self, tagid, session):
        asked_tag = session.query(Tag).filter_by(id=tagid).one()
        if asked_tag in self.tags:
            raise IrmaDatabaseError("Adding an already present Tag")
        self.tags.append(asked_tag)

    def remove_tag(self, tagid, session):
        asked_tag = session.query(Tag).filter_by(id=tagid).one()
        if asked_tag not in self.tags:
            raise IrmaDatabaseError("Removing a not present Tag")
        self.tags.remove(asked_tag)

    @classmethod
    def load_from_sha256(cls, sha256, session):
        """Find the object in the database, update data if file
           was previously deleted
        :param sha256: the sha256 to look for
        :param session: the session to use
        :rtype: cls
        :return: the object that corresponds to the sha256
        :raise: IrmaDatabaseResultNotFound, IrmaDatabaseError,
                IrmaFileSystemError
        """
        try:
            asked_file = session.query(cls).filter(
                cls.sha256 == sha256
            ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)
        # Check if file is still present
        if asked_file.path is not None and not os.path.exists(asked_file.path):
            asked_file.path = None
        return asked_file

    def remove_file_from_fs(self):
        """Remove the sample
        :raise: IrmaFileSystemError if there is a problem with the filesystem
        """
        try:
            if self.path is None:
                log.debug("%s File already deleted", self.sha256)
                return
            log.debug("Removing %s", self.path)
            os.remove(self.path)
        except OSError:
            log.info("%s File already deleted", self.sha256)
        finally:
            self.path = None

    def get_tags(self):
        results = []
        for t in self.tags:
            results.append(t.to_json())
        return results

    @classmethod
    def remove_old_files(cls, max_age, session):
        """Remove the files that are older than timestamp() - max_age
        from the file system
        :param max_age: the files older than timestamp() - max_age
            will be deleted
        :param session: SQLA session
        :rtype: int
        :return: the number of deleted files
        """
        fl = session.query(cls).filter(
            cls.timestamp_last_scan < compat.timestamp() - max_age
        ).filter(
            cls.path.isnot(None)
        ).all()
        for f in fl:
            f.remove_file_from_fs()
        session.commit()
        return len(fl)

    @classmethod
    def remove_files_max_size(cls, max_size, session):
        """Remove the oldest files from the file system if the max_size has
        been exceeded
        :param max_size: the space in bytes dedicated to the file system
        :param session: SQLA session
        :rtype: int
        return: the number of deleted files
        """
        # Construct a column "total" containing the sum of the size
        # of the younger files
        subq = session.query(cls,
                             func.sum(cls.size)
                             .over(order_by=cls.timestamp_last_scan
                                   .desc())
                             .label('total')).filter(
                                 cls.path.isnot(None)).subquery()
        cte = aliased(cls, subq, name='cte')
        fl = session.query(cte).filter(subq.c.total >= max_size).all()
        for f in fl:
            f.remove_file_from_fs()
        session.commit()
        return len(fl)

    @property
    def filenames(self):
        """Fetch the different names of the file
        :rtype: list
        :return: list of filenames
        """
        names = []
        for file_ext in self.files_ext:
            names.append(file_ext.name)
        return list(set(names))

    def get_ref_result(self, probe_name):
        # Get the last proberesult for the file
        session = inspect(self).session
        query = session.query(ProbeResult).join(File)
        query = query.filter(File.id == self.id)
        query = query.filter(ProbeResult.name == probe_name)
        query = query.order_by(desc(ProbeResult.id))
        ref_result = query.first()
        return ref_result

    @classmethod
    def get_or_create(cls, fileobj, session):
        """ Retrieve a File if already present in DB otherwise
        create a new entry.

        :param fileobj: file-like object containing file data
        :param session: database session
        :return: File object
        """
        sha256 = sha256sum(fileobj)
        # split files between subdirs
        path = build_sha256_path(sha256)
        try:
            # The file exists
            log.debug("try opening file with sha256: %s", sha256)
            file = File.load_from_sha256(sha256, session)
            if file.path is None:
                log.debug("file sample missing writing it")
                save_to_file(fileobj, path)
                file.path = path
        except IrmaDatabaseResultNotFound:
            # It doesn't
            file = cls.create(fileobj, sha256, path, session)
        return file

    @classmethod
    def create(cls, fileobj, sha256, path, session):
        try:
            # Create a new file
            time = compat.timestamp()
            sha1 = sha1sum(fileobj)
            md5 = md5sum(fileobj)
            # determine file mimetype
            magic = Magic()
            # magic only deal with buffer
            # feed it with a 4MB buffer
            mimetype = magic.from_buffer(fileobj.read(2 ** 22))
            size = save_to_file(fileobj, path)
            log.debug("not present, saving, sha256 %s sha1 %s"
                      "md5 %s size %s mimetype: %s",
                      sha256, sha1, md5, size, mimetype)
            file = File(sha256, sha1, md5, size, mimetype, path, time, time)
            session.add(file)
            session.commit()
            return file
        except IntegrityError as e:
            try:
                session.rollback()
                file = File.load_from_sha256(sha256, session)
                log.debug("Integrity error but load "
                          "successful for file.%s", sha256)
                return file
            except NoResultFound:
                log.debug("Integrity error load failed for file.%s", sha256)
                pass
            log.error(
                "Database integrity error: refuse to insert file.%s. %s",
                sha256,
                e,
            )
            raise IrmaDatabaseError("Integrity error")
