import typer


def success(message: str) -> None:
    typer.secho(f"\u2713 {message}", fg=typer.colors.GREEN)


def error(message: str) -> None:
    typer.secho(f"\u2717 {message}", fg=typer.colors.RED, err=True)


def warning(message: str) -> None:
    typer.secho(f"! {message}", fg=typer.colors.YELLOW)
