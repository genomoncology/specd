import os
import tempfile
from specd import tasks, utils, SpecDir


def test_convert_file_to_specd_json():
    with tempfile.TemporaryDirectory() as output_specd:
        input_file = os.path.join(os.path.dirname(__file__), "petstore.yaml")
        tasks.convert_file_to_specd(input_file, output_specd, "json")

        spec_dir = SpecDir(output_specd)
        assert spec_dir.format == "json"

        # check meta file contents
        meta = utils.file_path_to_dict(input_file)
        paths = meta.pop("paths")
        definitions = meta.pop("definitions")
        assert spec_dir.meta.read() == meta

        # check definitions
        for definition in spec_dir.definitions():
            assert definition.name in definitions
            assert definition.read() == definitions.get(definition.name)

        # check paths
        assert len(paths) == 2
        for path in spec_dir.paths():
            assert path.url in paths
            path_spec = paths.get(path.url)
            for operation in path.operations():
                assert operation.method in path_spec
                assert operation.read() == path_spec.get(operation.method)


def test_convert_file_to_specd_json_to_yaml():
    with tempfile.TemporaryDirectory() as output_specd:
        input_file = os.path.join(os.path.dirname(__file__), "petstore.json")
        tasks.convert_file_to_specd(input_file, output_specd, "yaml")

        spec_dir = SpecDir(output_specd)
        assert spec_dir.format == "yaml"

        # check meta file contents
        meta = utils.file_path_to_dict(input_file)
        paths = meta.pop("paths")
        definitions = meta.pop("definitions")
        assert spec_dir.meta.read() == meta

        # check definitions
        for definition in spec_dir.definitions():
            assert definition.name in definitions
            assert definition.read() == definitions.get(definition.name)

        # check paths
        assert len(paths) == 14
        for path in spec_dir.paths():
            assert path.url in paths
            path_spec = paths.get(path.url)
            for operation in path.operations():
                assert operation.method in path_spec
                assert operation.read() == path_spec.get(operation.method)

        assert tasks.validate_specd(output_specd) is None


def test_check_for_invalid_specd():
    with tempfile.TemporaryDirectory() as output_specd:
        input_file = os.path.join(os.path.dirname(__file__), "petstore.json")
        tasks.convert_file_to_specd(input_file, output_specd, "yaml")
        spec_dir = SpecDir(output_specd)

        spec_dir.meta.write({"swagger": "2.0"})
        msg = tasks.validate_specd(output_specd)
        assert msg == "'info' is a required property"


def test_convert_specd_to_file():
    with tempfile.TemporaryDirectory() as output_specd:
        input_file = os.path.join(os.path.dirname(__file__), "petstore.json")
        tasks.convert_file_to_specd(input_file, output_specd, "yaml")

        fp = os.path.join(output_specd, "out.json")
        tasks.convert_specd_to_file(output_specd, fp)
        spec = utils.file_path_to_dict(fp)

        assert spec == SpecDir(output_specd).as_dict()

        # now run again and thus trigger merge logic
        tasks.convert_file_to_specd(input_file, output_specd, "yaml")
        assert spec == SpecDir(output_specd).as_dict()


def test_check_for_not_a_specd():
    with tempfile.TemporaryDirectory() as output_specd:
        msg = tasks.validate_specd(output_specd)
        assert msg == f"Not in a valid specd root directory: {output_specd}"


def test_check_diff():
    with tempfile.TemporaryDirectory() as spec_dir:
        f = os.path.join(os.path.dirname(__file__), "petstore.json")
        tasks.convert_file_to_specd(f, spec_dir, "yaml")

        spec_file = os.path.join(os.path.dirname(__file__), "petstore.yaml")

        diffs = tasks.diff_specifications(spec_dir, spec_file)
        assert diffs.keys() == {("definitions", "Pet")}


def test_list_specd():
    with tempfile.TemporaryDirectory() as output_specd:
        input_file = os.path.join(os.path.dirname(__file__), "petstore.json")
        tasks.convert_file_to_specd(input_file, output_specd, "yaml")

        collect = tasks.list_specd(output_specd)
        assert (
            collect
            == [
                "\n\tDefinitions:\n",
                "\t\tApiResponse",
                "\t\tCategory",
                "\t\tOrder",
                "\t\tPet",
                "\t\tTag",
                "\t\tUser",
                "\n\tPaths:\n",
                "\t\t/pet/findByStatus: get",
                "\t\t/pet/findByTags: get",
                "\t\t/pet/{petId}/uploadImage: post",
                "\t\t/pet/{petId}: delete, get, post",
                "\t\t/pet: post, put",
                "\t\t/store/inventory: get",
                "\t\t/store/order/{orderId}: delete, get",
                "\t\t/store/order: post",
                "\t\t/user/createWithArray: post",
                "\t\t/user/createWithList: post",
                "\t\t/user/login: get",
                "\t\t/user/logout: get",
                "\t\t/user/{username}: delete, get, put",
                "\t\t/user: post",
            ]
        )


def test_create_definitions():
    with tempfile.TemporaryDirectory() as input_dir:
        spec_dir = tasks.create_specd(input_dir)
        input_file = os.path.join(os.path.dirname(__file__), "book.json")
        input_data = open(input_file).read()

        definitions = tasks.create_definitions(input_dir, "Book", input_data)
        assert len(definitions) == 11
        assert len(spec_dir.definitions()) == 11
        assert set([d.name for d in definitions]) == {
            "Book",
            "BookAuthor",
            "BookClassification",
            "BookCover",
            "BookEbook",
            "BookEbookFormat",
            "BookIdentifier",
            "BookPublishPlace",
            "BookPublisher",
            "BookSubject",
            "BookTableOfContent",
        }
