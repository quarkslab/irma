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

from datetime import datetime
from irma.common.utils.hash import sha256sum
from irma.common.utils.utils import timestamp
from irma.common.plugins import PluginLoadError
from irma.common.plugin_result import PluginResult

from pathlib import Path


class AntivirusPluginInterface(object):
    """ Antivirus Plugin Base Class
        Abstract class, should not be instanciated directly"""

    def __init__(self):
        self.module = self.module_cls()

    def run(self, paths):
        assert self.module
        if isinstance(paths, (tuple, list, set)):
            raise NotImplementedError(
                "Scanning of multiple paths at once is not supported for now")
        fpath = Path(paths)

        results = PluginResult(name=type(self).plugin_display_name,
                               type=type(self).plugin_category,
                               version=self.module.version)
        try:
            # add database metadata
            results.database = None
            if self.module.database:
                results.database = {str(fp): self.file_metadata(fp)
                                    for fp in self.module.database}
            # launch an antivirus scan, automatically append scan results
            started = timestamp(datetime.utcnow())
            results.status = self.module.scan(fpath)
            stopped = timestamp(datetime.utcnow())
            results.duration = stopped - started

            return_results = self.module.scan_results[fpath]
            # add scan results or append error
            if results.status < 0:
                results.error = return_results
            else:
                results.results = return_results

            # Add virus_database_version metadata
            results.virus_database_version = self.module.virus_database_version
        except Exception as e:
            results.status = -1
            results.error = type(e).__name__ + " : " + str(e)
        return results

    @staticmethod
    def file_metadata(fpath):
        metadata = {}
        if fpath.exists():
            metadata['mtime'] = fpath.stat().st_mtime
            metadata['ctime'] = fpath.stat().st_ctime
            try:
                with fpath.open('rb') as fd:
                    metadata['sha256'] = sha256sum(fd)
            except Exception:
                metadata['sha256'] = None
        return metadata

    @classmethod
    def verify(cls):
        return cls._chk_scanpath()

    @classmethod
    def _chk_scanpath(cls):
        module = cls.module_cls(early_init=False)
        e = PluginLoadError(
                "{}: verify() failed because {} executable was not found."
                .format(cls.__name__, cls._plugin_name_))
        try:
            module.scan_path
        except Exception:
            raise e

        if not module.scan_path or not module.scan_path.exists():
            raise e
