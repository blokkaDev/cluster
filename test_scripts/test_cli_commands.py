from typer.testing import CliRunner

from cli.cli import app

runner = CliRunner()


def test_help_shows_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("connect", "list", "load", "run", "start"):
        assert command in result.output


def test_connect_success(fake_client):
    result = runner.invoke(
        app, ["connect", "192.168.1.10", "8000", "sekret-token", "worker-1"]
    )
    assert result.exit_code == 0
    assert "connected" in result.output
    assert fake_client.calls == [
        ("connect", "192.168.1.10", 8000, "sekret-token", "worker-1", True)
    ]


def test_connect_missing_args(fake_client):
    result = runner.invoke(app, ["connect", "192.168.1.10"])
    assert result.exit_code == 2
    assert fake_client.calls == []


def test_connect_client_error(fake_client):
    fake_client.connect_result = {"error": "token rejected"}
    result = runner.invoke(
        app, ["connect", "192.168.1.10", "8000", "bad-token", "worker-1"]
    )
    assert result.exit_code == 1
    assert "token rejected" in result.output


def test_load_success(fake_client):
    result = runner.invoke(app, ["load", "worker-1", "sekret-token"])
    assert result.exit_code == 0
    assert "loaded" in result.output
    assert fake_client.calls == [("load", "worker-1", "sekret-token")]


def test_load_missing_args(fake_client):
    result = runner.invoke(app, ["load", "worker-1"])
    assert result.exit_code == 2
    assert fake_client.calls == []


def test_run_without_python_flag(fake_client, tmp_path):
    script = tmp_path / "script.py"
    script.write_text("print('hi')")

    result = runner.invoke(app, ["run", "worker-1", str(script)])
    assert result.exit_code == 1
    assert "Specify a language with --python" in result.output
    assert fake_client.calls == []


def test_run_missing_file_argument(fake_client, tmp_path):
    missing = tmp_path / "does_not_exist.py"

    result = runner.invoke(app, ["run", "worker-1", str(missing), "--python"])
    assert result.exit_code == 2
    assert fake_client.calls == []


def test_run_success(fake_client, tmp_path):
    script = tmp_path / "script.py"
    script.write_text("print('hi')")

    result = runner.invoke(app, ["run", "worker-1", str(script), "--python"])
    assert result.exit_code == 0
    assert "executed successfully" in result.output
    assert fake_client.calls == [
        ("execute", "print('hi')", "worker-1", "python")
    ]


def test_start_manager_success(fake_client):
    fake_client.start_result = {"state": True, "node": "manager"}
    result = runner.invoke(app, ["start", "--manager"])
    assert result.exit_code == 0
    assert "Manager started" in result.output
    assert fake_client.calls == [("start", True)]


def test_start_worker_success(fake_client):
    fake_client.start_result = {"state": True, "node": "worker"}
    result = runner.invoke(app, ["start", "--worker"])
    assert result.exit_code == 0
    assert "Worker started" in result.output
    assert fake_client.calls == [("start", False)]


def test_unknown_command(fake_client):
    result = runner.invoke(app, ["frobnicate"])
    assert result.exit_code == 2
    assert fake_client.calls == []
