#
# Copyright (c) 2013-2016 Quarkslab.
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

from marshmallow import Schema, fields


class ApiErrorSchema_v1(Schema):
    class Meta:
        fields = ("type", "message")


class FileSchema_v1(Schema):
    class Meta:
        fields = ("sha256", "sha1", "md5", "timestamp_first_scan",
                  "timestamp_last_scan", "size", "id")


def get_context_formatted(obj, context):
    return obj.get_probe_results(context['formatted'])


class FileWebSchema_v1(Schema):
    result_id = fields.String(attribute="external_id")
    file_infos = fields.Nested(FileSchema_v1, attribute="file")
    probe_results = fields.Function(get_context_formatted)
    scan_id = fields.Nested('ScanSchema_v1', attribute="scan", only='id')

    class Meta:
        fields = ("name",
                  "result_id",
                  "scan_id",
                  "file_infos",
                  "probe_results",
                  "probes_total",
                  "probes_finished",
                  "status")


class ScanSchema_v1(Schema):
    id = fields.String(attribute="external_id")
    results = fields.Nested(FileWebSchema_v1, attribute="files_web", many=True,
                            exclude=('probe_results', 'file_infos'))

    class Meta:
        fields = ("id", "date", "status", "probes_total", "probes_finished",
                  "results")
