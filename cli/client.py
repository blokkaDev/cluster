import json
import socket
from urllib import request
from urllib.error import HTTPError, URLError

from data.env import Env
from data.sqlite import Database

from .output import error

env = Env()
db = Database()


class ACSClient:
    def __init__(self):
        self.list(refresh=True)

        self._manager_thread = None
        self._worker_thread = None

    def _json(self, path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _post(self, url, data, report_errors: bool = True):
        req = request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            body = e.read().decode()
            if report_errors:
                error(f"HTTP {e.code}: {body}")
            raise
        except URLError as e:
            return {
                "error": (
                    "The Manager may not be running or the configured host/port "
                    "may be incorrect. Check: Manager host, Manager port, "
                    "network connectivity, Manager status."
                ),
                "debug": str(e.reason),
            }

    def _manager_url(self, path):
        host = self.manager.get("host", "127.0.0.1")
        port = self.manager.get("port", 8001)
        return f"http://{host}:{port}{path}"

    def _refresh_workers(self):
        self.workers = {}
        for worker in db.get_workers():
            try:
                self.workers[worker[1]] = {
                    "acs_hostname": worker[6],
                    "host": worker[4],
                    "port": worker[3],
                    "token": worker[5],
                    "last_seen": worker[8],
                    "status": worker[2],
                }
            except urllib.error.URLError as e:
                pass
        return self.workers

    def list(self, refresh: bool = False):
        env.get_all()

        self.manager = env.ManagerJson
        self.worker = env.WorkerJson

        if refresh:
            self._refresh_workers()
        return self.workers

    def connect(
        self, host: str, port: int, token: str, name: str, remember: bool = True
    ):
        return self._post(
            self._manager_url(f"/connect/{name}"),
            {
                "token": token,
                "remember": remember,
                "manager_token": self.manager.get("token"),
                "ip": host,
                "port": str(port),
            },
        )

    def load(self, worker_id: str, token: str):
        return self._post(
            self._manager_url(f"/load/{worker_id}"),
            {
                "token": token,
                "manager_token": self.manager.get("token"),
            },
        )

    def execute(self, code, worker_id, language="python"):
        try:
            return self._post(
                self._manager_url(f"/execute/{worker_id}"),
                {
                    "token": str(self.workers[worker_id].get("token")),
                    "manager_token": self.manager.get("token"),
                    "language": language,
                    "code": code,
                    "return_ip": self.manager.get("host", "127.0.0.1"),
                    "return_port": str(self.manager.get("port", 8001)),
                    "host": self.workers[worker_id].get("host", "0.0.0.0"),
                    "port": str(self.workers[worker_id].get("port", 8000)),
                },
                report_errors=False,
            )
        except Exception as e:
            error(str(e))
            return {
                "error": e,
            }

    def _run_manager(self):
        import uvicorn

        from machines import manager

        uvicorn.run(
            manager.app,
            host=self.manager.get("host", "0.0.0.0"),
            port=self.manager.get("port", 8001),
            log_config=None,
        )

    def _run_worker(self):
        import uvicorn

        from machines import worker

        uvicorn.run(
            worker.app,
            host=self.worker.get("host", "0.0.0.0"),
            port=self.worker.get("port", 8000),
            log_config=None,
        )

    def start(self, manager=None):
        if manager is True:
            if self._manager_thread and self._manager_thread.is_alive():
                return {"state": True, "node": "manager", "status": "already_running"}

            print(
                f"Starting Manager... on: http://{self.manager.get('host', '0.0.0.0')}:{self.manager.get('port', '8001')}"
            )
            self._run_manager()

            return {
                "state": True,
                "node": "manager",
                "host": self.manager.get("host", "0.0.0.0"),
                "port": self.manager.get("port", 8001),
            }

        if manager is False:
            if self._worker_thread and self._worker_thread.is_alive():
                return {"state": True, "node": "worker", "status": "already_running"}

            print(
                f"Starting Worker... on: http://{self.worker.get('host', '0.0.0.0')}:{self.worker.get('port', '8001')}"
            )
            self._run_worker()

            return {
                "state": True,
                "node": "worker",
                "host": self.worker.get("host", "0.0.0.0"),
                "port": self.worker.get("port", 8000),
            }

        return {"state": False, "error": "Specify --manager or --worker"}
