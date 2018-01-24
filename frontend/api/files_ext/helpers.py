from .schemas import FileExtSchema, FileCliSchema, FileProbeResultSchema, \
    FileSuricataSchema
from .models import FileExt, FileWeb, FileCli, FileProbeResult, FileSuricata

# Factory helpers for FileExt

file_ext_schemas = {
    FileExt.submitter_type: FileExtSchema,
    FileWeb.submitter_type: FileExtSchema,
    FileCli.submitter_type: FileCliSchema,
    FileProbeResult.submitter_type: FileProbeResultSchema,
    FileSuricata.submitter_type: FileSuricataSchema,
}


def get_file_ext_schemas(submitter):
    schema = file_ext_schemas[submitter]
    return schema()


def new_file_ext(submitter, file, filename, payload):
    if submitter == FileWeb.submitter_type:
        return FileWeb(file, filename)
    elif submitter == FileCli.submitter_type:
        return FileCli(file, filename)
    elif submitter == FileSuricata.submitter_type:
        return FileSuricata(file, filename, payload)
    else:
        raise ValueError("Unknown submitter")
