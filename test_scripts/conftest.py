import pytest

from cli import cli as cli_module


class FakeClient:
    """Stand-in for ACSClient. Records every call it receives and
    returns configurable canned responses, so CLI tests never touch
    the network, sqlite db, or the Env/dotenv-backed config."""

    def __init__(self):
        self.calls = []
        self.connect_result = {"state": True}
        self.list_result = {}
        self.load_result = {"state": True}
        self.execute_result = {"output": "ok"}
        self.start_result = {"state": True, "node": "manager"}

    def connect(self, host, port, token, name, remember=True):
        self.calls.append(("connect", host, port, token, name, remember))
        return self.connect_result

    def list(self, refresh=False):
        self.calls.append(("list", refresh))
        return self.list_result

    def load(self, worker_id, token):
        self.calls.append(("load", worker_id, token))
        return self.load_result

    def execute(self, code, worker_id, language="python"):
        self.calls.append(("execute", code, worker_id, language))
        return self.execute_result

    def start(self, manager=None):
        self.calls.append(("start", manager))
        return self.start_result


@pytest.fixture
def fake_client(monkeypatch):
    """Monkeypatches cli.cli.get_client so every command under test
    receives a FakeClient instead of a real ACSClient. Returns the
    FakeClient instance so tests can set canned results or inspect
    the calls it recorded."""
    client = FakeClient()
    monkeypatch.setattr(cli_module, "get_client", lambda: client)
    return client
