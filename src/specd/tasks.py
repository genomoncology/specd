import os
import typing

import click
from dictdiffer import diff
from swagger_spec_validator import validator20, SwaggerValidationError

from .model import SpecDir, Path, Operation, Definition
from .utils import file_path_to_dict, str_to_dict
from .walker import generate_definitions


def convert_file_to_specd(input_file: str, output_specd: SpecDir, format: str):
    input_spec = file_path_to_dict(input_file)
    spec_dir = SpecDir(output_specd, format)

    # write paths
    for (url, path_spec) in input_spec.pop("paths", {}).items():
        path = Path(spec_dir=spec_dir, url=url)
        for (method, operation_spec) in path_spec.items():
            operation = Operation(spec_dir=spec_dir, path=path, method=method)
            if operation.exists():
                click.echo(f"Operation exists, merging: {path} / {method}")
                operation.merge(operation_spec)
            else:
                operation.write(operation_spec)

    # write definitions
    for (name, def_spec) in input_spec.pop("definitions", {}).items():
        definition = Definition(spec_dir=spec_dir, name=name)

        if definition.exists():
            click.echo(f"Definition exists, merge: {name}")
            definition.merge(def_spec)
        else:
            definition.write(def_spec)

    # write meta (e.g. not paths or definitions)
    if spec_dir.meta.exists():
        click.echo(f"Meta found found, skipping.")
    else:
        spec_dir.meta.write(input_spec)


def guess_format(output_file):
    return os.path.splitext(output_file)[-1][1:] if output_file else "json"


def convert_specd_to_file(
    input_dir: str,
    output_file: str,
    targets: typing.List[str] = None,
    format: str = None,
):
    spec_dir = SpecDir(input_dir)
    assert spec_dir.exists(), f"Specd not found: {input_dir}"

    format = format or guess_format(output_file)
    spec_str = spec_dir.as_str(format, targets)

    if output_file:
        file_handler = open(output_file, "w+")
        file_handler.write(spec_str)
        file_handler.close()
    else:
        click.echo(spec_str)  # pragma: no cover


def validate_specd(input_dir: str) -> str:
    error_message = None

    try:
        spec_dir = SpecDir(input_dir)

        if spec_dir.exists():
            validator20.validate_spec(spec_dir.as_dict())
        else:
            error_message = f"Not in a valid specd root directory: {input_dir}"

    except SwaggerValidationError as e:
        error_message = e.args[0].split("\n")[0]

    return error_message


def get_spec_dict(item: str) -> dict:
    if os.path.isfile(item):
        spec_dict = file_path_to_dict(item)
    else:
        spec_dict = SpecDir(item).as_dict()

    return spec_dict


def get_dict_paths(d: dict):
    for defn in d.get("definitions", {}):
        yield ("definitions", defn)

    for url, spec in d.get("paths", {}).items():
        for operation in spec:
            yield ("paths", url, operation)


def resolve(d: dict, keys):
    for key in keys:
        d = d[key]
    return d


def diff_specifications(one, two):
    one = get_spec_dict(one)
    two = get_spec_dict(two)

    overlaps = set(get_dict_paths(one)).intersection(set(get_dict_paths(two)))

    diffs = {}
    for keys in overlaps:
        delta = list(diff(resolve(one, keys), resolve(two, keys)))
        diffs[keys] = delta

    return diffs


def list_specd(input_dir: str):
    spec_dir = SpecDir(input_dir)
    assert spec_dir.exists(), f"Specd not found: {input_dir}"

    collect = []
    defns = sorted([f"\t\t{d.name}" for d in spec_dir.definitions()])
    if defns:
        collect += ["\n\tDefinitions:\n"] + defns

    paths = sorted([f"\t\t{p.url}: {p.methods}" for p in spec_dir.paths()])
    if paths:
        collect += ["\n\tPaths:\n"] + paths
    return collect


def create_definitions(input_dir: str, name: str, input_data: str):
    spec_dir = SpecDir(input_dir)
    assert spec_dir.exists(), f"Specd not found: {input_dir}"

    data_dict = str_to_dict(input_data)
    definitions = []
    for definition in generate_definitions(name, data_dict):
        print(f"Writing Definition: {definition.name}")
        defn = Definition(spec_dir=spec_dir, name=definition.name)
        defn.write(definition.properties)
        definitions.append(defn)
    return definitions


def create_specd(input_dir: str):
    spec_dir = SpecDir(input_dir)
    spec_dir.meta.write({})
    return spec_dir
