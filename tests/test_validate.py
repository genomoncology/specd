from swagger_spec_validator import validator20, SwaggerValidationError
import os
import json


def test_validation():
    file_path = os.path.join(os.path.dirname(__file__), "petstore.json")
    spec_json = open(file_path).read()
    spec_dict = json.loads(spec_json)
    validator20.validate_spec(spec_dict)


def test_failed_validation():
    try:
        validator20.validate_spec(dict(swagger="2.0"))
    except SwaggerValidationError as e:
        assert isinstance(e, SwaggerValidationError)
        message = e.args[0].split("\n")[0]
        assert message == "'info' is a required property"
