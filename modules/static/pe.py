# Partially taken from cuckoo
import logging, os, pefile, peutils
from lib.common.mimetypes import Magic

log = logging.getLogger(__name__)

# code partially taken from cuckoo
class PE(object):

    def __init__(self, filepath=None, data=None, sigs=None):
        self.filepath = filepath
        self.data = data
        self.pe = None
        if sigs:
            self.sigs = peutils.SignatureDatabase(sigs)
        else:
            self.sigs = None

    def _get_filetype(self, data):
        try:
            filetype = Magic.from_buffer(data)
        except Exception as e:
            log.exception(e)
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
                section["name"] = convert_to_printable(entry.Name.strip("\x00"))
                section["virtual_address"] = "0x{0:08x}".format(entry.VirtualAddress)
                section["virtual_size"] = "0x{0:08x}".format(entry.Misc_VirtualSize)
                section["size_of_data"] = "0x{0:08x}".format(entry.SizeOfRawData)
                section["entropy"] = entry.get_entropy()
                sections.append(section)
            except:
                continue

        return sections

    def _get_resources(self):
        if not self.pe:
            return None

        resources = []

        if hasattr(self.pe, "DIRECTORY_ENTRY_RESOURCE"):
            for resource_type in self.pe.DIRECTORY_ENTRY_RESOURCE.entries:
                try:
                    resource = {}

                    if resource_type.name is not None:
                        name = str(resource_type.name)
                    else:
                        name = str(pefile.RESOURCE_TYPE.get(resource_type.struct.Id))

                    if hasattr(resource_type, "directory"):
                        for resource_id in resource_type.directory.entries:
                            if hasattr(resource_id, "directory"):
                                for resource_lang in resource_id.directory.entries:
                                    data = self.pe.get_data(resource_lang.data.struct.OffsetToData, resource_lang.data.struct.Size)
                                    filetype = self._get_filetype(data)
                                    language = pefile.LANG.get(resource_lang.data.lang, None)
                                    sublanguage = pefile.get_sublang_name_for_lang(resource_lang.data.lang, resource_lang.data.sublang)

                                    resource["name"] = name
                                    resource["offset"] = "0x{0:08x}".format(resource_lang.data.struct.OffsetToData)
                                    resource["size"] = "0x{0:08x}".format(resource_lang.data.struct.Size)
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
        if hasattr(self.pe, "VS_VERSIONINFO"):
            if hasattr(self.pe, "FileInfo"):
                for entry in self.pe.FileInfo:
                    try:
                        if hasattr(entry, "StringTable"):
                            for st_entry in entry.StringTable:
                                for str_entry in st_entry.entries.items():
                                    entry = {}
                                    entry["name"] = convert_to_printable(str_entry[0])
                                    entry["value"] = convert_to_printable(str_entry[1])
                                    infos.append(entry)
                        elif hasattr(entry, "Var"):
                            for var_entry in entry.Var:
                                if hasattr(var_entry, "entry"):
                                    entry = {}
                                    entry["name"] = convert_to_printable(var_entry.entry.keys()[0])
                                    entry["value"] = convert_to_printable(var_entry.entry.values()[0])
                                    infos.append(entry)
                    except:
                        continue

        return infos

    def analyze(self):
        if (self.filepath and self.data) or (not self.filepath and not self.data):
            log.error("either filepath ({0}) and data ({1}) should be set".format(self.filepath, self.data))
            return None
        elif self.filepath and not os.path.exists(self.filepath):
            log.error("file {0} does not exist".format(self.filepath))
            return None

        try:
            if self.filepath:
                self.pe = pefile.PE(self.filepath)
            elif self.data:
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
        results["imported_dll_count"] = len([x for x in results["pe_imports"] if x.get("dll")])

        return results
