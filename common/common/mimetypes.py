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

"""Wrapper for python-magic module

This wrapper handles python-magic api changes
"""
import magic
import os


class Magic(object):
    """Factory class for python-magic"""

    # ==================
    #  internal helpers
    # ==================

    @classmethod
    def _initialize(cls,
                    magic_file=None,
                    mime=False,
                    mime_encoding=False,
                    keep_going=False):
        """Initialize python-magic"""
        # setting flags
        cls.flags = magic.MAGIC_NONE
        if mime:
            cls.flags |= magic.MAGIC_MIME
        if mime_encoding:
            cls.flags |= magic.MAGIC_MIME_ENCODING
        if keep_going:
            cls.flags |= magic.MAGIC_CONTINUE
        # creating cookie
        cls.old_api = True
        try:
            # using the old API
            cls.cookie = magic.open(cls.flags)
            # load database
            if magic_file and os.path.exists(magic_file):
                cls.cookie.load(magic_file)
            else:
                cls.cookie.load()
        except AttributeError:
            cls.old_api = False
            cls.cookie = magic.Magic(mime=mime,
                                     magic_file=magic_file,
                                     mime_encoding=mime_encoding,
                                     keep_going=keep_going)
            cls.cookie.file = cls.cookie.from_file
            cls.cookie.buffer = cls.cookie.from_buffer

    # ================
    #  Public methods
    # ================

    @classmethod
    def from_buffer(cls, buf, **kwargs):
        """Compute mimetype from a buffer

        :param buf: buffer from where to get data
        """
        cls._initialize(**kwargs)
        # perform processing
        try:
            filetype = cls.cookie.buffer(buf)
            if cls.old_api:
                cls.cookie.close()
        except magic.MagicException:
            # should never enter here, but in case of
            filetype = None
        return filetype

    @classmethod
    def from_file(cls, filename, **kwargs):
        """Compute mimetype from file

        :param filename: name of a file from where to get data
        """
        # reconfigure class before processing
        cls._initialize(**kwargs)
        # perform processing
        try:
            filetype = cls.cookie.file(filename)
            if cls.old_api:
                cls.cookie.close()
        except magic.MagicException:
            # should never enter here, but in case of
            filetype = None
        return filetype
