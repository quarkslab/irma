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
import json
import os
import pprint

from abc import ABCMeta

# HACK: to avoid an error on import if leveldict is not installed
try:
    from leveldict import LevelDictSerialized
except ImportError as e:
    # use type and not metaclass because of the singleton
    LevelDictSerialized = type

from irma.common.utils.oopatterns import ParametricSingletonMetaClass

log = logging.getLogger(__name__)


# =============
#  Serializers
# =============

class NSRLSerializer(object):

    fields = None

    @classmethod
    def loads(cls, value):
        value = json.loads(value)
        if isinstance(value[0], list):
            result = [dict((field, col[index])
                              for index, field in
                              enumerate(cls.fields)) for col in value]
        else:
            result = dict((field, value[index])
                          for index, field in
                          enumerate(cls.fields))
        return result

    @classmethod
    def dumps(cls, value):

        def detect_charset(string):
            import chardet
            return chardet.detect(string)['encoding']

        try:
            if isinstance(value, list):
                result = json.dumps([[row.get(key) for key in cls.fields] for row in value])
            else:
                result = json.dumps([value.get(col) for col in cls.fields])
        except Exception:
            if isinstance(value, list):
                for row in value:
                    for colkey, colval in list(row.items()):
                        if not isinstance(colval, str):
                            charset = detect_charset(colval)
                            if charset is None:
                                charset = 'unicode-escape'
                            try:
                                row[colkey] = colval.decode(charset)
                            except:
                                row[colkey] = colval.decode('unicode-escape')
                result = json.dumps([[row.get(key) for key in cls.fields] for row in value])
            else:
                for colkey, colval in list(value.items()):
                    if not isinstance(colval, str):
                        # try to use chardet to find encoding
                        charset = detect_charset(colval)
                        if charset is None:
                            charset = 'unicode-escape'
                        try:
                            value[colkey] = colval.decode(charset)
                        except:
                            # treat false positive from chardet
                            value[colkey] = colval.decode('unicode-escape')
                result = json.dumps([value.get(col) for col in cls.fields])
        return result


class NSRLOsSerializer(NSRLSerializer):

    fields = ['OpSystemVersion', 'OpSystemName', 'MfgCode']


class NSRLFileSerializer(NSRLSerializer):

    fields = ["MD5", "CRC32", "FileName", "FileSize",
              "ProductCode", "OpSystemCode", "SpecialCode"]

    @classmethod
    def dumps(cls, value):

        def detect_charset(string):
            import chardet
            return chardet.detect(string)['encoding']

        try:
            if isinstance(value, list):
                result = json.dumps([[row.get(key) for key in cls.fields] for row in value])
            else:
                result = json.dumps([value.get(col) for col in cls.fields])
        except Exception:
            # failed to json it, bruteforce encoding
            if isinstance(value, list):
                for row in value:
                    fname = row['FileName']
                    if not isinstance(fname, str):
                        charset = detect_charset(fname)
                        charset = 'unicode-escape' if not charset else charset
                        try:
                            row['FileName'] = fname.decode(charset)
                        except:
                            # treat false positive from chardet
                            row['FileName'] = fname.decode('unicode-escape')
                result = json.dumps([[col.get(key) for key in cls.fields] for col in value])
            else:
                fname = value['FileName']
                if not isinstance(fname, str):
                    # try to use chardet to find encoding
                    charset = detect_charset(fname)
                    charset = 'unicode-escape' if not charset else charset
                    try:
                        value['FileName'] = fname.decode(charset)
                    except:
                        # treat false positive from chardet
                        value['FileName'] = fname.decode('unicode-escape')
                result = json.dumps([value.get(col) for col in cls.fields])
        return result


class NSRLManufacturerSerializer(NSRLSerializer):

    fields = ["MfgName"]


class NSRLProductSerializer(NSRLSerializer):

    fields = ["ProductName", "ProductVersion", "OpSystemCode",
              "MfgCode", "Language", "ApplicationType"]


# ==============
#  NSRL records
# ==============

# Hack to avoid metaclass conflicts
class LevelDBSingletonMetaClass(ABCMeta, ParametricSingletonMetaClass):
    pass

LevelDBSingleton = LevelDBSingletonMetaClass('LevelDBSingleton', (object,), {})


class NSRLLevelDict(LevelDictSerialized, LevelDBSingleton):

    key = None

    @staticmethod
    def depends_on(cls, *args, **kwargs):
        # singleton depends on the uri parameter
        (db,) = args[0]
        return os.path.abspath(db)

    def __init__(self, db, serializer=json, **kwargs):
        super(NSRLLevelDict, self).__init__(db, serializer, **kwargs)

    @classmethod
    def create_database(cls, dbfile, records, **kwargs):
        # import specific modules
        from csv import DictReader

        log_threshold = 50000

        # create database
        db = cls(dbfile, **kwargs)
        # open csv files
        csv_file = open(records, 'r')
        csv_entries = DictReader(csv_file)

        for index, row in enumerate(csv_entries):
            key = row.pop(cls.key)
            value = db.get(key, None)
            if not value:
                db[key] = row
            else:
                if isinstance(value, dict):
                    db[key] = [value, row]
                else:
                    # db[key].append([row]) is not possible as changes are only
                    # made in memory and __setitem__ is never called
                    db[key] = value + [row]
            if (index % log_threshold) == 0:
                print(("Current progress: {0}".format(index)))

        return db


# ==================
#  NSRL File Record
# ==================

class NSRLFile(NSRLLevelDict):

    key = "SHA-1"

    def __init__(self, db, **kwargs):
        super(NSRLFile, self).__init__(db, NSRLFileSerializer, **kwargs)


# =================
#  NSRL OS Record
# =================

class NSRLOs(NSRLLevelDict):

    key = "OpSystemCode"

    def __init__(self, db, **kwargs):
        super(NSRLOs, self).__init__(db,
                                     NSRLOsSerializer,
                                     **kwargs)


# ================
#  NSRL OS Record
# ================

class NSRLManufacturer(NSRLLevelDict):

    key = "MfgCode"

    def __init__(self, db, **kwargs):
        super(NSRLManufacturer, self).__init__(db,
                                               NSRLManufacturerSerializer,
                                               **kwargs)


# =====================
#  NSRL Product Record
# =====================

class NSRLProduct(NSRLLevelDict):

    key = "ProductCode"

    def __init__(self, db, **kwargs):
        super(NSRLProduct, self).__init__(db,
                                          NSRLProductSerializer,
                                          **kwargs)


# =============
#  NSRL module
# =============

class NSRL(object):

    def __init__(self,
                 nsrl_file,
                 nsrl_product,
                 nsrl_os, nsrl_manufacturer,
                 **kwargs):
        # TODO: need to specify paths in constructor,
        # temporary pass via kwargs
        self.nsrl_file = NSRLFile(nsrl_file)
        self.nsrl_product = NSRLProduct(nsrl_product)
        self.nsrl_os = NSRLOs(nsrl_os)
        self.nsrl_manufacturer = NSRLManufacturer(nsrl_manufacturer)

    def _lookup_file(self, sha1sum):
        return self.nsrl_file[sha1sum]

    def _lookup_product(self, product_code):
        return self.nsrl_product[product_code]

    def _lookup_os(self, op_system_code):
        return self.nsrl_os[op_system_code]

    def _lookup_manufacturer(self, manufacturer_code):
        return self.nsrl_manufacturer[manufacturer_code]

    def lookup_by_sha1(self, sha1sum):
        operations = [
            (sha1sum, 'SHA-1', self.nsrl_file, None),
            (None, 'ProductCode', self.nsrl_product, 'SHA-1'),
            (None, 'OpSystemCode', self.nsrl_os, 'SHA-1'),
            (None, 'MfgCode', self.nsrl_manufacturer, 'ProductCode')
        ]
        entries = dict((name, {}) for (_, name, _, _) in operations)
        try:
            for value, key, database, where in operations:
                if value:
                    entries[key][value] = database[value]
                else:
                    subkeys = set()
                    for subkey, subitem in list(entries[where].items()):
                        if not isinstance(subitem, list):
                            subitem = [subitem]
                        subkeys.update([x[key] for x in subitem])
                    for subkey in subkeys:
                        entries[key][subkey] = database[subkey]
        except:
            pass
        return entries

##############################################################################
# CLI for debug purposes
##############################################################################

if __name__ == '__main__':

    ##########################################################################
    # local import
    ##########################################################################

    import argparse

    ##########################################################################
    # defined functions
    ##########################################################################

    nsrl_databases = {
        'file':         NSRLFile,
        'os':           NSRLOs,
        'manufacturer': NSRLManufacturer,
        'product':      NSRLProduct,
    }

    def nsrl_create_database(**kwargs):
        database_type = kwargs['type']
        nsrl_databases[database_type].create_database(kwargs['database'],
                                                      kwargs['filename'])

    def nsrl_get(**kwargs):
        database_type = kwargs['type']
        database = nsrl_databases[database_type](kwargs['database'],
                                                 block_cache_size=1 << 30,
                                                 max_open_files=3000)
        value = database.get(kwargs['key'])
        print(("key {0}: value {1}".format(kwargs['key'], value)))

    def nsrl_resolve(**kwargs):
        # TODO: handle in a better way NRSL object
        kwargs['nsrl_file_db'] = kwargs['file']
        kwargs['nsrl_prod_db'] = kwargs['product']
        kwargs['nsrl_os_db'] = kwargs['os']
        kwargs['nsrl_mfg_db'] = kwargs['manufacturer']
        handle = NSRL(**kwargs)
        print((pprint.pformat(handle.lookup_by_sha1(kwargs['sha1']))))

    ##########################################################################
    # arguments
    ##########################################################################

    # define command line arguments
    desc_msg = 'NSRL database module CLI mode'
    parser = argparse.ArgumentParser(description=desc_msg)
    parser.add_argument('-v',
                        '--verbose',
                        action='count',
                        default=0)
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the create parser
    help_msg = 'create NSRL records into a database'
    create_parser = subparsers.add_parser('create',
                                          help=help_msg)
    create_parser.add_argument('-t',
                               '--type',
                               type=str,
                               choices=['file', 'os',
                                        'manufacturer', 'product'],
                               help='type of the record')
    create_parser.add_argument('filename',
                               type=str,
                               help='filename of the NSRL record')
    create_parser.add_argument('database',
                               type=str,
                               help='database to store NSRL records')
    create_parser.set_defaults(func=nsrl_create_database)

    # create the scan parser
    get_parser = subparsers.add_parser('get',
                                       help='get the entry from database')
    get_parser.add_argument('-t',
                            '--type',
                            type=str,
                            choices=['file', 'os', 'manufacturer', 'product'],
                            help='type of the record')
    get_parser.add_argument('database',
                            type=str,
                            help='database to read NSRL records')
    get_parser.add_argument('key',
                            type=str,
                            help='key to retreive')
    get_parser.set_defaults(func=nsrl_get)

    # create the scan parser
    get_parser = subparsers.add_parser('resolve',
                                       help='resolve from sha1')
    get_parser.add_argument('file',
                            type=str,
                            help='filename for file records')
    get_parser.add_argument('product',
                            type=str,
                            help='filename for product records')
    get_parser.add_argument('os',
                            type=str,
                            help='filename for os records')
    get_parser.add_argument('manufacturer',
                            type=str,
                            help='filename for manufacturer records')
    get_parser.add_argument('sha1',
                            type=str,
                            help='sha1 to lookup')
    get_parser.set_defaults(func=nsrl_resolve)

    args = parser.parse_args()

    # set verbosity
    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.DEBUG)

    args = vars(parser.parse_args())
    func = args.pop('func')
    # with 'func' removed, args is now a kwargs
    # with only the specific arguments
    # for each subfunction useful for interactive mode.
    func(**args)
