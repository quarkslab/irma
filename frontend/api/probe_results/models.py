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

from api.common.format import IrmaFormatter

from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import relationship, backref

from api.common.models import Base, tables_prefix

# Many to many ProbeResult <-> FileExt
probe_result_file_ext = Table(
        '{0}probeResult_fileExt'.format(tables_prefix),
        Base.metadata,
        Column(
                'id_fe',
                Integer,
                # see FileExt.id_file
                ForeignKey('{0}fileExt.id'.format(tables_prefix)),
                index=True,
        ),
        # should be a PKF in FileExt
        # https://groups.google.com/forum/#!topic/sqlalchemy/TxISzgW7xUg
        # Column(
        #     'id_file',
        #     Integer
        # ),
        Column(
                'id_pr',
                Integer,
                ForeignKey('{0}probeResult.id'.format(tables_prefix))
        ),
        # See FileExt
        # ForeignKeyConstraint(   # Composite PFK from FileExt
        #     ['id_fw', 'id_file'],
        #     [
        #         '{0}fileExt.id_fw'.format(tables_prefix),
        #         '{0}fileExt.id_file'.format(tables_prefix)
        #     ]
        # )
)


class ProbeResult(Base):
    __tablename__ = '{0}probeResult'.format(tables_prefix)

    # Fields
    id = Column(
            Integer,
            autoincrement=True,
            nullable=False,
            primary_key=True,
            name='id'
    )
    type = Column(
            String,
            name='type'
    )
    name = Column(
            String,
            nullable=False,
            name='name'
    )
    doc = Column(
            JSONB,
            name='doc'
    )
    status = Column(
            Integer,
            name='status'
    )
    # Many to many ProbeResult <-> FileExt
    files_ext = relationship(
            'FileExt',
            secondary=probe_result_file_ext,
            backref='probe_results',
            lazy='dynamic',
    )
    # Many to one ProbeResult <-> File
    id_file = Column(
            Integer,
            ForeignKey('{0}file.id'.format(tables_prefix)),
            index=True
    )
    file = relationship(
            'File',
            backref=backref('results')
    )

    def __init__(self,
                 type,
                 name,
                 doc,
                 status,
                 files_ext=None):
        super(ProbeResult, self).__init__()

        self.type = type
        self.name = name
        self.doc = doc
        self.status = status
        self.files_ext = [files_ext]

    def get_details(self, formatted=True):
        res = self.doc.copy()
        res.pop('uploaded_files', '')
        # apply or not IrmaFormatter
        if formatted:
            res = IrmaFormatter.format(self.name, res)
        return res
