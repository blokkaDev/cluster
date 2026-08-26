from pathlib import Path

import typer

from .client import ACSClient

app = typer.Typer(name="acs", no_args_is_help=True)
client = ACSClient()


@app.command()
def connect(host: str, port: int, token: str, remember: bool = True):
    typer.echo(client.connect(host, port, token, remember))


@app.command()
def load(worker_id: str, token: str):
    typer.echo(client.load(worker_id, token))


@app.command()
def run(
    file: Path = typer.Argument(..., exists=True, readable=True, dir_okay=False),
    python: bool = typer.Option(False, "--python"),
):
    if not python:
        typer.echo("Specify a language with --python", err=True)
        raise typer.Exit(1)

    typer.echo(client.execute(file.read_text(), "python"))


@app.command()
def start(
    manager: bool = typer.Option(None, "--manager/--worker"),
):
    typer.echo(client.start(manager=manager))


if __name__ == "__main__":
    app()
