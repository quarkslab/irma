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

# Partially taken from cuckoo
import logging
import os

from irma.common.utils.mimetypes import Magic

log = logging.getLogger(__name__)


# code partially taken from cuckoo
class PE(object):

    def __init__(self):
        global pefile
        import pefile

        global peutils
        import peutils

    def _get_filetype(self, data):
        try:
            filetype = Magic.from_buffer(data)
        except Exception as e:
            log.exception(type(e).__name__ + " : " + str(e))
            filetype = None
        return filetype

    def _get_peid_signatures(self):
        if not self.pe or not self.sigs:
            return None

        try:
            return self.sigs.match(self.pe, ep_only=True)
        except:
            return None

    def _get_imported_symbols(self):
        if not self.pe:
            return None

        imports = []

        if hasattr(self.pe, "DIRECTORY_ENTRY_IMPORT"):
            for entry in self.pe.DIRECTORY_ENTRY_IMPORT:
                try:
                    symbols = []
                    for imported_symbol in entry.imports:
                        symbol = {}
                        symbol["address"] = hex(imported_symbol.address)
                        symbol["name"] = imported_symbol.name
                        symbols.append(symbol)

                    imports_section = {}
                    imports_section["dll"] = entry.dll
                    imports_section["imports"] = symbols
                    imports.append(imports_section)
                except:
                    continue

        return imports

    def _get_exported_symbols(self):
        if not self.pe:
            return None

        exports = []

        if hasattr(self.pe, "DIRECTORY_ENTRY_EXPORT"):
            for exported_symbol in self.pe.DIRECTORY_ENTRY_EXPORT.symbols:
                symbol = {}
                symbol["address"] = hex(self.pe.OPTIONAL_HEADER.ImageBase +
                                        exported_symbol.address)
                symbol["name"] = exported_symbol.name
                symbol["ordinal"] = exported_symbol.ordinal
                exports.append(symbol)

        return exports

    def _get_sections(self):
        if not self.pe:
            return None

        sections = []

        for entry in self.pe.sections:
            try:
                section = {}
                name = entry.Name.strip("\x00")
                section["name"] = name
                va = entry.VirtualAddress
                section["virtual_address"] = "0x{0:08x}".format(va)
                vsize = entry.Misc_VirtualSize
                section["virtual_size"] = "0x{0:08x}".format(vsize)
                srawdat = entry.SizeOfRawData
                section["size_of_data"] = "0x{0:08x}".format(srawdat)
                section["entropy"] = entry.get_entropy()
                sections.append(section)
            except:
                continue

        return sections

    def _get_resources(self):
        if not self.pe:
            return None

        resources = []
        if not hasattr(self.pe, "DIRECTORY_ENTRY_RESOURCE"):
            return resources

        for resource_type in self.pe.DIRECTORY_ENTRY_RESOURCE.entries:
            try:
                resource = {}

                if resource_type.name is not None:
                    name = str(resource_type.name)
                else:
                    struct_id = resource_type.struct.Id
                    name = str(pefile.RESOURCE_TYPE.get(struct_id))

                if not hasattr(resource_type, "directory"):
                    continue

                for resource_id in resource_type.directory.entries:
                    if not hasattr(resource_id, "directory"):
                        continue
                    for resource_lang in resource_id.directory.entries:

                        offset = resource_lang.data.struct.OffsetToData
                        size = resource_lang.data.struct.Size
                        lang = resource_lang.data.lang
                        sublang = resource_lang.data.sublang
                        data = self.pe.get_data(offset, size)
                        filetype = self._get_filetype(data)
                        language = pefile.LANG.get(lang, None)
                        sublanguage = pefile.get_sublang_name_for_lang(lang,
                                                                       sublang)
                        resource["name"] = name
                        resource["offset"] = "0x{0:08x}".format(offset)
                        resource["size"] = "0x{0:08x}".format(size)
                        resource["filetype"] = filetype
                        resource["language"] = language
                        resource["sublanguage"] = sublanguage
                        resources.append(resource)
            except:
                continue

        return resources

    def _get_versioninfo(self):
        if not self.pe:
            return None

        infos = []
        if not hasattr(self.pe, "VS_VERSIONINFO"):
            return infos
        if not hasattr(self.pe, "FileInfo"):
            return infos
        for entry in self.pe.FileInfo:
            try:
                if hasattr(entry, "StringTable"):
                    for st_entry in entry.StringTable:
                        for str_entry in st_entry.entries.items():
                            entry = {}
                            entry["name"] = str_entry[0]
                            entry["value"] = str_entry[1]
                            infos.append(entry)
                elif hasattr(entry, "Var"):
                    for var_entry in entry.Var:
                        if hasattr(var_entry, "entry"):
                            entry = {}
                            name = var_entry.entry.keys()[0]
                            entry["name"] = name
                            value = var_entry.entry.values()[0]
                            entry["value"] = value
                            infos.append(entry)
            except:
                continue

        return infos

    def analyze(self, filepath=None, data=None, sigs=None):
        self.filepath = filepath
        self.data = data
        self.pe = None
        if sigs:
            self.sigs = peutils.SignatureDatabase(sigs)
        else:
            self.sigs = None
        if (self.filepath and self.data is not None) or \
           (self.filepath is None and self.data is None):
            log.error("either filepath ({0}) ".format(self.filepath) +
                      "and data ({0}) should be set".format(self.data))
            return None
        elif self.filepath and not os.path.exists(self.filepath):
            log.error("file {0} does not exist".format(self.filepath))
            return None

        try:
            if self.filepath is not None:
                self.pe = pefile.PE(self.filepath)
            elif self.data is not None:
                self.pe = pefile.PE(data=self.data)
        except pefile.PEFormatError:
            return None

        results = {}
        results["peid_signatures"] = self._get_peid_signatures()
        results["pe_imports"] = self._get_imported_symbols()
        results["pe_exports"] = self._get_exported_symbols()
        results["pe_sections"] = self._get_sections()
        results["pe_resources"] = self._get_resources()
        results["pe_versioninfo"] = self._get_versioninfo()
        nb_dll = len([x for x in results["pe_imports"] if x.get("dll")])
        results["imported_dll_count"] = nb_dll

        return results
