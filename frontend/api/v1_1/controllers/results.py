from bottle import response, request
from frontend.api.v1_1.errors import process_error
from frontend.models.sqlobjects import FileWeb
from frontend.api.v1_1.schemas import FileWebSchema_v1_1
from frontend.helpers.utils import validate_id


def get(resultid, db):
    """ Retrieve a single fileweb result, with details.
        The request should be performed using a GET request method.
    """
    try:
        formatted = False if request.query.formatted == 'no' else True

        validate_id(resultid)
        fw = FileWeb.load_from_ext_id(resultid, db)

        file_web_schema = FileWebSchema_v1_1()
        file_web_schema.context = {'formatted': formatted}

        response.content_type = "application/json; charset=UTF-8"
        return file_web_schema.dumps(fw).data
    except Exception as e:
        process_error(e)
