from .schemas import FileExtSchema, FileCliSchema, FileKioskSchema, \
    FileProbeResultSchema, FileSuricataSchema
from .models import FileExt, FileWeb, FileCli, FileKiosk, FileProbeResult, \
    FileSuricata

# Factory helpers for FileExt

file_ext_schemas = {
    FileExt.submitter_type: FileExtSchema,
    FileWeb.submitter_type: FileExtSchema,
    FileCli.submitter_type: FileCliSchema,
    FileKiosk.submitter_type: FileKioskSchema,
    FileProbeResult.submitter_type: FileProbeResultSchema,
    FileSuricata.submitter_type: FileSuricataSchema,
}


def get_file_ext_schemas(submitter, **kwargs):
    schema = file_ext_schemas[submitter]
    return schema(**kwargs)


def new_file_ext(submitter, file, filename, payload):
    if submitter == FileWeb.submitter_type:
        return FileWeb(file, filename)
    elif submitter == FileCli.submitter_type:
        return FileCli(file, filename)
    elif submitter == FileKiosk.submitter_type:
        return FileKiosk(file, filename, payload)
    elif submitter == FileSuricata.submitter_type:
        return FileSuricata(file, filename, payload)
    else:
        raise ValueError("Unknown submitter")
