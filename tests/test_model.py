import tempfile
import os

from specd.model import SpecDir, Path, Operation, Definition, merge_dicts


def test_model_yaml():
    with tempfile.TemporaryDirectory() as root_dir:
        spec_dir = SpecDir(root=root_dir, default_format="yaml")
        assert spec_dir.format == "yaml"

        spec = dict(a=1, b=dict(c="a"), schemes=["http"])
        assert spec_dir.to_spec(spec_dir.to_str(spec)) == spec

        assert spec_dir.meta.file_name == "specd.yaml"
        assert spec_dir.meta.file_path == f"{root_dir}/specd.yaml"

        spec_dir.meta.write(spec)
        assert spec_dir.meta.read() == spec


def test_model_json():
    with tempfile.TemporaryDirectory() as root_dir:
        spec_dir = SpecDir(root=root_dir, default_format="json")
        assert spec_dir.format == "json"

        spec = dict(a=1, b=dict(c="a"), schemes=["http"])
        assert spec_dir.to_spec(spec_dir.to_str(spec)) == spec

        assert spec_dir.meta.file_name == "specd.json"
        assert spec_dir.meta.file_path == f"{root_dir}/specd.json"

        spec_dir.meta.write(spec)
        assert spec_dir.meta.read() == spec


def test_model_paths():
    with tempfile.TemporaryDirectory() as root_dir:
        spec_dir = SpecDir(root=root_dir, default_format="yaml")
        path = Path(spec_dir=spec_dir, url="/pets/{petId}")

        abspath = os.path.join(root_dir, "paths/pets/{petId}")
        assert path.abspath == abspath

        operation = Operation(spec_dir, path, "get")
        assert operation.file_name == "get.yaml"
        assert operation.file_path == os.path.join(abspath, "get.yaml")
        assert not operation.exists()

        spec = dict(a=1, b=dict(c="a"))
        operation.write(spec)
        assert operation.read() == spec
        assert operation.exists()

        assert len(path.operations()) == 1
        assert path.get_operation("get").read() == spec
        assert path.methods == "get"

        assert not path.get_operation("post").exists()


def test_model_definitions():
    with tempfile.TemporaryDirectory() as root_dir:
        spec_dir = SpecDir(root=root_dir, default_format="json")
        definition = Definition(spec_dir=spec_dir, name="NewPet")

        abspath = os.path.join(root_dir, "definitions/NewPet.json")
        assert definition.file_path == abspath
        assert not definition.exists()

        spec = dict(a=1, b=dict(c="a"))
        definition.write(spec)
        assert definition.exists()
        assert definition.read() == spec


def test_merge_dicts():
    dict1 = {1: {"a": "A"}, 2: {"b": "B"}}
    dict2 = {2: {"c": "C"}, 3: {"d": "D"}}
    merged = dict(merge_dicts(dict1, dict2))
    assert merged == {1: {"a": "A"}, 2: {"c": "C", "b": "B"}, 3: {"d": "D"}}
