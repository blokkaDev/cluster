from pathlib import Path

import dotenv


class Env:
    def __init__(self):
        self.path = Path(__file__).resolve().parent / "secrets" / ".env"
        self.env = dict(dotenv.dotenv_values(self.path))

        self.WorkerJson = {}
        self.ManagerJson = {}

    def get(self, key, default=None):
        return self.env.get(key, default)

    def get_all(self):
        data = self.env.copy()
        self.ManagerJson = {
            "token": data.get("MANAGER_TOKEN", None),
            "hostname": data.get("MANAGER_HOSTNAME", None),
            "port": int(data.get("MANAGER_PORT", None)),
            "remember": data.get("MANAGER_REMEMBER", None),
            "host": data.get("MANAGER_HOST", None),
        }
        self.WorkerJson = {
            "token": data.get("WORKER_TOKEN", None),
            "port": int(data.get("WORKER_PORT", None)),
            "hostname": data.get("WORKER_HOSTNAME", None),
            "host": data.get("WORKER_HOST", None),
            "id": data.get("WORKER_ID", None),
        }
        return data

    def set(self, key, value):
        self.env[key] = str(value) if value is not None else None
        self._save()

    def _save(self):
        lines = []

        for key, value in self.env.items():
            if value is not None:
                lines.append(f"{key}={value}")

        self.path.write_text(
            "\n".join(lines) + ("\n" if lines else ""),
            encoding="utf-8",
        )
