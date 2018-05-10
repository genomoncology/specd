import typing
import enum
import os
import re
import json

import yaml

from .utils import dict_to_str


@enum.unique
class FileFormat(enum.Enum):
    json = "json"
    yaml = "yaml"


class SpecDir(object):

    PATH_PATTERN = re.compile("^[\w/{}._]+$")
    DEF_PATTERN = re.compile("^[\w_]+$")

    def __init__(self, root: str, default_format: str = None):
        self.root: str = os.path.abspath(root)
        self.meta: Meta = Meta(self)
        self.format: str = self.meta.determine_format(default_format)

    # functions

    def exists(self):
        return self.meta.exists()

    def abspath(self, *args):
        args = [f"./{arg}" for arg in args]
        return os.path.abspath(os.path.join(self.root, *args))

    def to_str(self, spec: dict) -> str:
        return dict_to_str(spec, self.format)

    def to_spec(self, content: str) -> dict:
        if self.format == FileFormat.yaml.value:
            return yaml.load(content)
        else:
            return json.loads(content)

    def write_file(self, spec: dict, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_handle = open(file_path, "w+")
        file_handle.write(self.to_str(spec))
        file_handle.close()

    def read_file(self, file_path: str):
        file_handle = open(file_path, "rU")
        content_str = file_handle.read()
        file_handle.close()
        return self.to_spec(content_str)

    def definitions(self) -> typing.List["Definition"]:
        return [
            self.get_definition(name)
            for name in get_file_names(self.abspath(Definition.DEFINITIONS))
        ]

    def get_definition(self, name_or_filename):
        name = name_or_filename.split(".")[0]
        return Definition(self, name)

    def get_definition_map(self):
        return dict([(d.name, d) for d in self.definitions()])

    def paths(self) -> typing.List["Path"]:
        paths = []
        paths_root = self.abspath(Path.PATHS)
        for path, _, file_names in os.walk(paths_root):
            if file_names:
                url = path[len(paths_root):]
                paths.append(self.get_path(url))
        return paths

    def get_path(self, url: str) -> "Path":
        return Path(self, url)

    def find_definitions(self, spec: dict):
        for (key, value_) in spec.items():
            # (clever code warning) support descent into lists
            value_ = value_ if isinstance(value_, list) else [value_]

            for value in value_:
                if key == "$ref" and isinstance(value, str) and value:
                    yield value.split("/")[-1]

                elif isinstance(value, dict):
                    for definition in self.find_definitions(value):
                        yield definition

    def paths_as_dict(self, targets):
        paths = {}
        found_definitions = set()
        all_ops = (targets == set())

        for path in self.paths():
            path_spec = {}

            for operation in path.operations():
                op_spec = operation.read()
                op_targets = op_spec.pop("targets", set())
                if all_ops or (targets.intersection(op_targets)):
                    path_spec[operation.method] = op_spec
                    found_definitions.update(self.find_definitions(op_spec))

            if path_spec:
                paths[path.url] = path_spec

        return (paths, found_definitions)

    def definitions_as_dict(self, found_definitions):
        all_definitions = self.get_definition_map()
        result = {}
        next_round = found_definitions

        while next_round:
            this_round = next_round
            next_round = set()
            for name in this_round:
                def_spec = all_definitions.get(name).read()
                result[name] = def_spec

                for found_name in self.find_definitions(def_spec):
                    if found_name not in result:
                        next_round.add(found_name)

        return result

    def as_dict(self, targets=None):
        targets = set(targets or [])
        spec = self.meta.read()
        (spec["paths"], found_definitions) = self.paths_as_dict(targets)
        spec["definitions"] = self.definitions_as_dict(found_definitions)
        return spec

    def as_str(self, format, targets=None):
        return dict_to_str(self.as_dict(targets), format)


class Meta(object):

    FNAME = "specd"

    def __init__(self, spec_dir: SpecDir):
        self.spec_dir = spec_dir

    def determine_format(self, default_format: str) -> str:
        """ Returns format based on meta file, then default, then yaml. """
        is_json = os.path.exists(self.spec_dir.abspath(f"{self.FNAME}.json"))
        is_yaml = os.path.exists(self.spec_dir.abspath(f"{self.FNAME}.yaml"))
        assert not (is_json and is_yaml), "Corrupt: multiple meta files found."
        return (
            (is_json and FileFormat.json.value)
            or (is_yaml and FileFormat.yaml.value)
            or default_format
            or FileFormat.yaml.value
        )

    @property
    def file_name(self):
        return f"{self.FNAME}.{self.spec_dir.format}"

    @property
    def file_path(self):
        return self.spec_dir.abspath(self.file_name)

    def exists(self):
        return os.path.exists(self.file_path)

    def write(self, spec: dict):
        self.spec_dir.write_file(spec=spec, file_path=self.file_path)

    def read(self):
        spec = self.spec_dir.read_file(file_path=self.file_path)
        if "schemes" not in spec:
            spec["schemes"] = ["https", "http"]
        return spec


class Path(object):

    PATHS = "paths"

    def __init__(self, spec_dir: SpecDir, url: str):
        self.spec_dir = spec_dir
        self.url = url

    @property
    def abspath(self):
        return self.spec_dir.abspath(self.PATHS, self.url)

    def operations(self):
        return [
            self.get_operation(method)
            for method in get_file_names(self.abspath)
        ]

    def get_operation(self, method_or_filename):
        method = method_or_filename.split(".")[0]
        return Operation(self.spec_dir, self, method)

    @property
    def methods(self):
        return ", ".join(sorted([op.method for op in self.operations()]))


class Operation(object):

    def __init__(self, spec_dir: SpecDir, path: Path, method: str):
        self.spec_dir = spec_dir
        self.path = path
        self.method = method

    @property
    def file_name(self):
        return f"{self.method}.{self.spec_dir.format}"

    @property
    def file_path(self):
        return self.spec_dir.abspath(Path.PATHS, self.path.url, self.file_name)

    def exists(self):
        return os.path.exists(self.file_path)

    def write(self, spec: dict):
        self.spec_dir.write_file(spec=spec, file_path=self.file_path)

    def read(self):
        return self.spec_dir.read_file(file_path=self.file_path)

    def merge(self, spec: dict):
        original = self.read()
        merged = dict(merge_dicts(original, spec))
        self.write(merged)


class Definition(object):

    DEFINITIONS = "definitions"

    def __init__(self, spec_dir: SpecDir, name: str):
        self.spec_dir = spec_dir
        self.name = name

    @property
    def file_name(self):
        return f"{self.name}.{self.spec_dir.format}"

    @property
    def file_path(self):
        return self.spec_dir.abspath(self.DEFINITIONS, self.file_name)

    def exists(self):
        return os.path.exists(self.file_path)

    def write(self, spec: dict):
        self.spec_dir.write_file(spec=spec, file_path=self.file_path)

    def read(self):
        return self.spec_dir.read_file(file_path=self.file_path)

    def merge(self, spec: dict):
        original = self.read()
        merged = dict(merge_dicts(original, spec))
        self.write(merged)


def get_file_names(abspath):
    return [
        fn
        for fn in os.listdir(abspath)
        if os.path.isfile(os.path.join(abspath, fn))
    ]


def merge_dicts(dict1, dict2):
    """ https://stackoverflow.com/a/7205672/1946790 """
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(merge_dicts(dict1[k], dict2[k])))
            else:
                yield (k, dict2[k])
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])
