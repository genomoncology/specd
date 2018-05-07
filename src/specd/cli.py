import os
import sys
import pprint

import click

from . import tasks, create_app


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "input_file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.argument(
    "output_specd", type=click.Path(file_okay=False, resolve_path=True)
)
@click.option(
    "--format", "-f", type=click.Choice(["json", "yaml"]), default="yaml"
)
def convert(input_file, output_specd, format):
    """convert a specification file into a specd."""
    input_file = click.format_filename(input_file)
    output_specd = click.format_filename(output_specd)
    tasks.convert_file_to_specd(input_file, output_specd, format)


@cli.command()
@click.argument(
    "output_file",
    "output_specd",
    type=click.Path(dir_okay=False, resolve_path=True),
)
def generate(output_file):
    """create specification file from current specd."""
    input_dir = os.getcwd()
    output_file = click.format_filename(output_file)
    tasks.convert_specd_to_file(input_dir, output_file)


@cli.command()
def validate():
    """validate current specd project."""
    input_dir = os.getcwd()
    error_message = tasks.validate_specd(input_dir)
    if error_message:
        click.echo(f"Validation failed: {error_message}")
        sys.exit(1)
    else:
        click.echo("Successfully validated.")


@cli.command()
@click.option("--host", "-h", default=None)
@click.option("--name", "-n", default=None)
def swagger(host, name):
    """start a flask app for swagger UI."""
    create_app(include_swagger=True, host=host, name=name).run()


@cli.command()
@click.argument("one", type=click.Path(exists=True, resolve_path=True))
@click.argument("two", type=click.Path(exists=True, resolve_path=True))
def diff(one, two):
    """show path/defn differences between two specs."""
    one = click.format_filename(one)
    two = click.format_filename(two)
    click.echo(f"diff: {one} & {two}")
    result = tasks.diff_specifications(one, two)

    for (keys, value) in result.items():
        for key in keys:
            click.echo(f"{key} > ", nl=False)
        if value:
            print("Diff")
            pprint.pprint(value, indent=6, width=120, depth=5)
        else:
            print("Same")


if __name__ == "__main__":
    cli()
