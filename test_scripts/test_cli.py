from typer.testing import CliRunner
from cli.cli import app, client

runner=CliRunner()

def test_list_with_workers():
    fake_workers={"idd-1": {"host": "192.168.1.10","port": 8001,"acs_hostname": "acs.worker-idd-1.local","status": "ONLINE","last_seen": "just now"},
        "idd-2": {"host": "192.168.1.20","port": 8001,"acs_hostname": "acs.worker-idd-2.local","status": "OFFLINE","last_seen": "3m ago"}
        }
    
    def get_fake_workers():
        return fake_workers
    client.list=get_fake_workers

    result= runner.invoke(app, ["list"])
    assert result.exit_code == 0

    assert "idd-1" in result.output
    assert "192.168.1.10" in result.output
    assert "ONLINE" in result.output
    
    assert "idd-2" in result.output
    assert "192.168.1.20" in result.output
    assert "! OFFLINE !" in result.output
    assert "3m ago" in result.output

    assert "8001" in result.output

