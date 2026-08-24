import json
import threading
from urllib import request
from urllib.error import HTTPError

from pathlib import Path


class ACSClient:
    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parent.parent
        
        self.main = self._json(BASE_DIR / "data" / "main.json")
        self.workers = self._json(BASE_DIR / "data" / "workers.json")
        self.worker_id = self.main.get("worker")
        self.worker = self.workers.get(
            self.worker_id,
            self.workers.get("lastWorker", {})
        )

        self.manager = self._json(BASE_DIR / "data" / "manager.json")
        self._manager_thread = None
        self._worker_thread = None

    def _json(self, path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _post(self, url, data):
        req = request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            body = e.read().decode()
            print(f"HTTP ERROR: {e.code}")
            print(f"RESPONSE: {body}")
            raise

    def _manager_url(self, path):
        host = self.manager.get("ip", "127.0.0.1")
        port = self.manager.get("port", 8001)
        return f"http://{host}:{port}{path}"

    def connect(self):
        return self._post(
            self._manager_url(f"/connect/{self.worker_id}"),
            {
                "token": self.worker.get("token"),
                "remember": self.manager.get("remember", True),
                "manager_token": self.manager.get("token"),
                "ip": "127.0.0.1",
                "port": str(self.worker.get("port", 8000)),
            }
        )

    def load(self):
        return self._post(
            self._manager_url(f"/load/{self.worker_id}"),
            {
                "token": self.worker.get("token"),
                "manager_token": self.manager.get("token"),
            }
        )

    def execute(self, code, language="python"):
        return self._post(
            self._manager_url(f"/execute/{self.worker_id}"),
            {
                "token": self.worker.get("token"),
                "manager_token": self.manager.get("token"),
                "language": language,
                "code": code,
                "return_ip": self.manager.get("ip", "127.0.0.1"),
                "return_port": str(self.manager.get("port", 8001)),
            }
        )

    def _run_manager(self):
        import uvicorn
        import machines.manager as manager

        uvicorn.run(
            manager.app,
            host=self.manager.get("host", "0.0.0.0"),
            port=self.manager.get("port", 8001),
            log_config=None
        )

    def _run_worker(self):
        import uvicorn
        import machines.worker as worker

        uvicorn.run(
            worker.app,
            host=self.worker.get("host", "0.0.0.0"),
            port=self.worker.get("port", 8000),
            log_config=None
        )

    def start(self, manager=None):
        if manager is True:
            if self._manager_thread and self._manager_thread.is_alive():
                return {"state": True, "node": "manager", "status": "already_running"}

            self._manager_thread = threading.Thread(
                target=self._run_manager,
                daemon=True
            )
            self._manager_thread.start()

            return {
                "state": True,
                "node": "manager",
                "host": self.manager.get("host", "0.0.0.0"),
                "port": self.manager.get("port", 8001)
            }

        if manager is False:
            if self._worker_thread and self._worker_thread.is_alive():
                return {"state": True, "node": "worker", "status": "already_running"}

            self._worker_thread = threading.Thread(
                target=self._run_worker,
                daemon=True
            )
            self._worker_thread.start()

            return {
                "state": True,
                "node": "worker",
                "host": self.worker.get("host", "0.0.0.0"),
                "port": self.worker.get("port", 8000)
            }

        return {"state": False, "error": "Specify --manager or --worker"}
