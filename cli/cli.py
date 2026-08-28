from pathlib import Path

import typer

from .client import ACSClient

app = typer.Typer(name="acs", no_args_is_help=True)
client = ACSClient()


@app.command()
def connect(host: str, port: int, token: str, name: str, remember: bool = True):
    typer.echo(client.connect(host, port, token, name, remember))


@app.command()
def list():
    workers=client.list()
    if len(workers)==0:
        typer.echo("No workers connected.")
        return
    typer.echo("ID\t    HOST\t  PORT\t  STATUS\t    LAST SEEN\t HOSTNAME")
    typer.echo("-"*60)

    for worker_id,info in workers.items():
        host=info.get("host","Not found")
        port=str(info.get("port","Not found"))
        hostname=info.get("acs_hostname","Not found" )
        status=str(info.get("status","ONLINE")).upper()
        if status== "OFFLINE":
            status="! OFFLINE !"
        last_seen=info.get("last_seen", "Not found")
        typer.echo(f"{worker_id}\t  {host}\t    {port}\t    {status}\t  {last_seen}\t   {hostname}")


@app.command()
def load(worker_id: str, token: str):
    typer.echo(client.load(worker_id, token))


@app.command()
def run(
    worker_id: str,
    file: Path = typer.Argument(..., exists=True, readable=True, dir_okay=False),
    python: bool = typer.Option(False, "--python"),
):
    if not python:
        typer.echo("Specify a language with --python", err=True)
        raise typer.Exit(1)

    typer.echo(client.execute(file.read_text(), worker_id, "python"))


@app.command()
def start(
    manager: bool = typer.Option(None, "--manager/--worker"),
):
    typer.echo(client.start(manager=manager))


if __name__ == "__main__":
    app()
