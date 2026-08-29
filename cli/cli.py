from pathlib import Path

import typer

from .client import ACSClient
from .output import error, success, warning

app = typer.Typer(name="acs", no_args_is_help=True)
client = ACSClient()


@app.command()
def connect(host: str, port: int, token: str, name: str, remember: bool = True):
    result = client.connect(host, port, token, name, remember)
    if isinstance(result, dict) and result.get("error"):
        error(f"Unable to connect to Manager: {result['error']}")
        raise typer.Exit(1)
    success(f"Worker '{name}' connected")
    typer.echo(result)


@app.command()
def list():
    workers=client.list()
    if len(workers)==0:
        warning("No workers connected.")
        return
    typer.echo("ID\t    HOST\t  PORT\t  STATUS\t    LAST SEEN\t HOSTNAME")
    typer.echo("-"*60)

    for worker_id,info in workers.items():
        host=info.get("host","Not found")
        port=str(info.get("port","Not found"))
        hostname=info.get("acs_hostname","Not found" )
        status=str(info.get("status","ONLINE")).upper()
        if status== "OFFLINE":
            status=typer.style("! OFFLINE !", fg=typer.colors.RED)
        else:
            status=typer.style(status, fg=typer.colors.GREEN)
        last_seen=info.get("last_seen", "Not found")
        typer.echo(f"{worker_id}\t  {host}\t    {port}\t    {status}\t  {last_seen}\t   {hostname}")


@app.command()
def load(worker_id: str, token: str):
    result = client.load(worker_id, token)
    if isinstance(result, dict) and result.get("error"):
        error(f"Unable to load worker: {result['error']}")
        raise typer.Exit(1)
    success(f"Worker '{worker_id}' loaded")
    typer.echo(result)


@app.command()
def run(
    worker_id: str,
    file: Path = typer.Argument(..., exists=True, readable=True, dir_okay=False),
    python: bool = typer.Option(False, "--python"),
):
    if not python:
        error("Specify a language with --python")
        raise typer.Exit(1)
    
    result = client.execute(file.read_text(), worker_id, "python")
    if isinstance(result, dict) and result.get("error"):
        error(f"Execution failed: {result['error']}")
        raise typer.Exit(1)
    success("Code executed successfully")
    typer.echo(result)


@app.command()
def start(
    manager: bool = typer.Option(None, "--manager/--worker"),
):
    result = client.start(manager=manager)
    if isinstance(result, dict) and result.get("error"):
        error(str(result["error"]))
        raise typer.Exit(1)
    typer.echo(result)


if __name__ == "__main__":
    app()
