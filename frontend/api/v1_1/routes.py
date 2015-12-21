#
# Copyright (c) 2013-2015 QuarksLab.
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

from frontend.api.v1_1.controllers import probes, files, scans, results, tags


""" Define all routes for the API
    This file is loaded by base.py
"""


def define_routes(application):
    # probes routes
    application.route("/probes", callback=probes.list)
    # scans routes
    application.route("/scans",
                      callback=scans.list)
    application.route("/scans", method="POST",
                      callback=scans.new)
    application.route("/scans/<scanid>",
                      callback=scans.get)
    application.route("/scans/<scanid>/files", method="POST",
                      callback=scans.add_files)
    application.route("/scans/<scanid>/launch", method="POST",
                      callback=scans.launch)
    application.route("/scans/<scanid>/cancel", method="POST",
                      callback=scans.cancel)
    application.route("/scans/<scanid>/results",
                      callback=scans.get_results)
    application.route("/results/<resultid>",
                      callback=results.get)
    # tags routes
    application.route("/tags",
                      callback=tags.list_available_tags)
    # files routes
    application.route("/files",
                      callback=files.list)
    # files routes
    application.route("/files/<sha256>",
                      callback=files.get)
    application.route("/files/<sha256>/tags/<tagid>/add",
                      callback=files.add_tag)
    application.route("/files/<sha256>/tags/<tagid>/remove",
                      callback=files.remove_tag)
