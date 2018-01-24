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

import sqlalchemy
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from irma.common.exceptions import IrmaValueError, IrmaDatabaseResultNotFound
from irma.common.exceptions import IrmaDatabaseError


class SQLDatabaseObject(object):
    """Mother class for the SQL tables
    """

    __tablename__ = None
    _idname = None

    # Fields
    # In the subclasses, the variables names must be the same has fields
    # names without the suffix except for the foreign keys and PFKs
    # Ex for a PK or field : var name: some_field
    #                        field name: some_field_suffix
    # Ex for a FK or PFK : var name: some_key
    #                      key name: some_key
    id = None

    def __init__(self):
        if type(self) is SQLDatabaseObject:
            reason = "The SQLDatabaseObject class has to be overloaded"
            raise IrmaValueError(reason)

    def to_dict(self, include_pks=True, include_fks=True, columns_list=None):
        """Converts object to dict.
        :rtype: dict
        """
        res = {}
        if columns_list is None:
            columns_list = []
            for column in self.__table__.columns:
                # table name removal (fixed length)
                item = str(column)[len(self.__tablename__ + '.'):]
                columns_list.append(item)

        pk_names_list = []
        if not include_pks:
            for pk in self.__mapper__.primary_key:
                pk_names_list.append(pk.name)

        fk_names_list = []
        if not include_fks:
            for fk in self.__table__.foreign_keys:
                # table name removal (various length)
                fk_names_list.append(fk.target_fullname.rsplit('.', 1)[1])

        for key in columns_list:
            if getattr(self, key) is not None:
                if (not include_pks and key in pk_names_list) or\
                        (not include_fks and key in fk_names_list):
                    continue
                res[key] = getattr(self, key)
        return res

    def update(self, columns_list=None, session=None):
        """Save the new state of the current object in the database
        :param update_dict: the fields to update (all fields are being
            updated if not provided)
        :param session: the session to use
        """
        update_dict = self.to_dict(include_pks=False,
                                   columns_list=columns_list)
        session.query(self.__class__).\
            filter(self.__class__.id == self.id).\
            update(update_dict)

    def save(self, session):
        """Save the current object in the database
        :param session: the session to use
        """
        session.add(self)

    @classmethod
    def query_fields(cls):
        fields = {}
        for (name, column) in cls.__table__.columns.items():
            if column.primary_key:
                continue
            if len(column.foreign_keys) > 0:
                continue
            fields[name] = column
        return fields

    @classmethod
    def load(cls, id, session):
        """Load an object from the database
        :param id: the id to look for
        :param session: the session to use
        :rtype: cls
        :return: the object that corresponds to the id
        :raise IrmaDatabaseResultNotFound: if the object doesn't exist
        """
        try:
            return cls.find_by_id(id, session=session)
        except Exception:
            raise IrmaDatabaseResultNotFound(
                "The given id ({0}) doesn't exist in {1}".format(
                    id, cls.__tablename__
                )
            )

    def remove(self, session):
        """Remove the current object from the database
        :param session: the session to use
        """
        session.delete(self)

    @classmethod
    def find_by_id(cls, id, session):
        """Find the object in the database
        :param id: the id to look for
        :param session: the session to use
        :rtype: cls
        :return: the object that corresponds to the id
        :raise IrmaDatabaseResultNotFound, IrmaDatabaseError
        """
        try:
            return session.query(cls).filter(
                cls.id == id
            ).one()
        except NoResultFound as e:
            raise IrmaDatabaseResultNotFound(e)
        except MultipleResultsFound as e:
            raise IrmaDatabaseError(e)

    @classmethod
    def paginate(cls, query, page=None, page_size=None,
                 order_by=None, desc=False):
        """Paginate query
        :param query a sqlalchemy query with all filtering done
        :param page skip page * page_size items in results
        :param page_size nb of items returned
        :param order_by results are sorted by this column
               due to join not known, should be checked by caller
        :param rev_order boolean to switch order_by ordering
        :rtype: dict
        :return: a key:value dict with returned objects
        :raise IrmaDatabaseError
        """
        res = dict()
        res['total'] = query.count()
        if order_by is not None:
            if desc:
                order_by = sqlalchemy.desc(order_by)
            query = query.order_by(order_by)
        if page_size is not None:
            try:
                page_size = int(page_size)
            except ValueError:
                raise IrmaValueError("wrong argument for page_size")
        else:
            page_size = 25
        query = query.limit(page_size)
        if page is not None and page > 0:
            try:
                page = int(page) - 1
            except ValueError:
                raise IrmaValueError("wrong argument for page")
            query = query.offset(page * page_size)
        res['items'] = []
        for row in query.all():
            dict_row = dict((k, row[i]) for i, k in enumerate(row.keys()))
            res['items'].append(dict_row)
        return res

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return str(self.to_dict())
