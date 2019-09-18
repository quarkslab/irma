#
# Extracted and adapted from
# https://github.com/yohanboniface/falcon-multipart/blob/master/falcon_multipart/middleware.py
#
# MIT License
#
# Copyright (c) 2017 Yohan Boniface
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

import cgi
import falcon


class MultipartMiddleware:

    def __init__(self, parser=None):
        self.parser = parser or cgi.FieldStorage

    def parse(self, stream, environ):
        return self.parser(fp=stream, environ=environ)

    def parse_field(self, field):
        if isinstance(field, list):
            return [self.parse_field(subfield) for subfield in field]

        # When file name isn't ascii FieldStorage will not consider it.
        encoded = field.disposition_options.get('filename*')
        if encoded:
            # NOTE: http://stackoverflow.com/a/93688
            encoding, filename = encoded.split("''")
            field.filename = filename
        if getattr(field, 'filename', False):
            return field
        # This is not a file, thus get flat value (not
        # FieldStorage instance).
        return field.value

    def process_request(self, req, resp, **kwargs):

        if 'multipart/form-data' not in (req.content_type or ''):
            return

        # This must be done to avoid a bug in cgi.FieldStorage.
        req.env.setdefault('QUERY_STRING', '')

        # To avoid all stream consumption problem which occurs in falcon 1.0.0
        # or above.
        stream = (req.stream.stream if hasattr(req.stream, 'stream') else
                  req.stream)
        try:
            form = self.parse(stream=stream, environ=req.env)
        except ValueError as e:  # Invalid boundary?
            raise falcon.HTTPBadRequest('Error parsing file', str(e))

        for key in form:
            # TODO: put files in req.files instead when #418 get merged.
            req._params[key] = self.parse_field(form[key])
