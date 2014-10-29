#
# Copyright (c) 2013-2014 QuarksLab.
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

from marshmallow import Serializer, fields


class FileSerializer(Serializer):
    class Meta:
        fields = ("sha256", "sha1", "md5", "timestamp_first_scan",
                  "timestamp_last_scan", "size")


class ScanSerializer(Serializer):
    class Meta:
        fields = ["external_id"]


class FileWebSerializer(Serializer):
    file = fields.Nested(FileSerializer)
    scan = fields.Nested(ScanSerializer)

    class Meta:
        fields = ("name", "scan_file_idx", "file", "scan")
