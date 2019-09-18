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

from marshmallow import Schema, fields
from api.probe_results.schemas import ProbeResultSchema


def get_context_formatted(obj, context):
    if context["api_version"] == 1:
        results_as = "list"
    else:
        results_as = "dict"
    return obj.get_probe_results(context['formatted'], results_as=results_as)


class FileExtSchema(Schema):
    result_id = fields.String(attribute="external_id")
    file_infos = fields.Nested('FileSchema', attribute="file")
    file_sha256 = fields.Nested('FileSchema', attribute="file",
                                only='sha256')
    probe_results = fields.Function(get_context_formatted)
    scan_id = fields.Nested('ScanSchema', attribute="scan",
                            only='id')
    scan_date = fields.Nested('ScanSchema', attribute="scan",
                              only='date')
    parent_file_sha256 = fields.Nested('FileSchema', attribute="parent",
                                       only='sha256')
    other_results = fields.Nested('FileExtSchema',
                                  only=("result_id", "scan_date", "status"),
                                  many=True)

    class Meta:
        fields = ("result_id",
                  "name",
                  "file_sha256",
                  "parent_file_sha256",
                  "scan_id",
                  "scan_date",
                  "file_infos",
                  "probe_results",
                  "probes_total",
                  "probes_finished",
                  "status",
                  "submitter",
                  "other_results",
                  )


class FileCliSchema(FileExtSchema):

    class Meta(FileExtSchema.Meta):
        fields = FileExtSchema.Meta.fields + ("path",)


class FileKioskSchema(FileExtSchema):

    class Meta(FileExtSchema.Meta):
        fields = FileExtSchema.Meta.fields + ("path", "submitter_id",)


class FileProbeResultSchema(FileExtSchema):
    probe_parent = fields.Nested('ProbeResultSchema',
                                 attribute="probe_result_parent")

    class Meta(FileExtSchema.Meta):
        fields = FileExtSchema.Meta.fields + ("probe_parent",)


class FileSuricataSchema(FileExtSchema):

    class Meta(FileExtSchema.Meta):
        fields = FileExtSchema.Meta.fields + ("context",)
