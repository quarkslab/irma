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


class ScanSchema(Schema):
    id = fields.String(attribute="external_id")
    results = fields.Nested('FileExtSchema', attribute="files_ext",
                            many=True,
                            exclude=('probe_results', 'file_infos',
                                     'other_results'))

    class Meta:
        fields = ("id", "date", "status", "probes_total",
                  "probes_finished",
                  "results", "force", "mimetype_filtering", "resubmit_files")
