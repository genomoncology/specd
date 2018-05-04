import os
import click

from swagger_spec_validator import validator20, SwaggerValidationError

from .model import SpecDir, Path, Operation, Definition
from .utils import file_path_to_dict


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


def convert_specd_to_file(input_dir: str, output_file: str):
    spec_dir = SpecDir(input_dir)
    assert spec_dir.exists(), f"Specd not found: {input_dir}"

    format = os.path.splitext(output_file)[-1][1:]
    spec_str = spec_dir.as_str(format)

    file_handler = open(output_file, "w+")
    file_handler.write(spec_str)
    file_handler.close()


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
