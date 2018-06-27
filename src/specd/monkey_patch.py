import os
from bravado_core.exception import SwaggerMappingError
from bravado_core import param


def add_file(param, value, request):
    """Add a parameter of type 'file' to the given request.

    :type param: :class;`bravado_core.param.Param`
    :param value: The raw content of the file to be uploaded
    :type request: dict
    """
    if request.get("files") is None:
        # support multiple files by default by setting to an empty array
        request["files"] = []

        # The http client should take care of setting the content-type header
        # to 'multipart/form-data'. Just verify that the swagger spec is
        # conformant
        expected_mime_type = "multipart/form-data"

        if expected_mime_type not in param.op.consumes:
            raise SwaggerMappingError(
                (
                    "Mime-type '{0}' not found in list of supported "
                    "mime-types for "
                    "parameter '{1}' on operation '{2}': {3}"
                ).format(
                    expected_mime_type,
                    param.name,
                    param.op.operation_id,
                    param.op.consumes,
                )
            )

    if isinstance(value, tuple):
        filename, val = value
    else:
        filename, val = param.name, value

    _, filename = os.path.split(val.name)
    file_tuple = (param.name, (filename, val))
    request["files"].append(file_tuple)


param.add_file = add_file
