#
# Copyright (c) 2013-2018 QuarksLab.
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


class SQLConf:

    def __init__(self, *, dbms, dialect=None, username=None, password=None,
                 host=None, port=None, dbname='', tables_prefix=None,
                 sslmode="disable", sslrootcert=None, sslcert=None,
                 sslkey=None):
        self.dbms = dbms
        self.dialect = dialect
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname
        self.tables_prefix = tables_prefix
        self.sslmode = sslmode
        self.sslrootcert = sslrootcert
        self.sslcert = sslcert
        self.sslkey = sslkey

    @property
    def url(self):
        authority = ""
        if self.host:
            userinfo = ""
            if self.username:
                passwordf = ""
                if self.password:
                    passwordf = ":" + self.password
                userinfo = self.username + passwordf + "@"
            portf = ""
            if self.port:
                portf = ":{}".format(self.port)
            authority = userinfo + self.host + portf

        scheme = self.dbms
        if self.dialect:
            scheme += "+" + self.dialect

        return "{}://{}/{}".format(scheme, authority, self.dbname)
