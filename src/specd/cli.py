import os
import sys

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
    """generate a JSON version"""
    input_dir = os.getcwd()
    output_file = click.format_filename(output_file)
    tasks.convert_specd_to_file(input_dir, output_file)


@cli.command()
def validate():
    input_dir = os.getcwd()
    error_message = tasks.validate_specd(input_dir)
    if error_message:
        click.echo(f"Validation failed: {error_message}")
        sys.exit(1)
    else:
        click.echo("Successfully validated.")


@cli.command()
def swagger():
    create_app(include_swagger=True).run()


if __name__ == "__main__":
    cli()
