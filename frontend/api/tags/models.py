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

from sqlalchemy import Table, Column, Integer, String, ForeignKey, \
    UniqueConstraint
from sqlalchemy.orm import relationship
from api.common.models import Base, tables_prefix

# Many to many Tag <-> File
tag_file = Table(
        '{0}tag_file'.format(tables_prefix),
        Base.metadata,
        Column(
                'id_tag',
                Integer,
                ForeignKey('{0}tag.id'.format(tables_prefix))
        ),
        Column(
                'id_file',
                Integer,
                ForeignKey('{0}file.id'.format(tables_prefix))),
        UniqueConstraint('id_tag', 'id_file', name='u_tag_file')
)


class Tag(Base):
    __tablename__ = '{0}tag'.format(tables_prefix)

    # Fields
    id = Column(
        Integer,
        autoincrement=True,
        nullable=False,
        primary_key=True,
        name='id'
    )
    text = Column(
        String,
        nullable=False,
        name='text'
    )

    # Many to many Tag <-> File
    files = relationship(
        'File',
        secondary=tag_file,
        backref='tags',
        lazy='dynamic',
    )

    def __init__(self, text=''):
        super(Tag, self).__init__()
        self.text = text

    def to_json(self):
        # get name and remove tablename prefix
        columns = (str(c).split('.', 1)[1] for c in self.__table__.columns)
        return {c: getattr(self, c) for c in columns if getattr(self, c)}

    @classmethod
    def query_find_all(cls, session):
        return session.query(Tag).all()
