import sys
from pathlib import Path

import dotenv


class Env:
    REQUIRED_MANAGER_VARS = [
        "MANAGER_TOKEN",
        "MANAGER_HOST",
        "MANAGER_PORT",
        "MANAGER_HOSTNAME",
    ]
    REQUIRED_WORKER_VARS = [
        "WORKER_ID",
        "WORKER_TOKEN",
        "WORKER_HOST",
        "WORKER_PORT",
        "WORKER_HOSTNAME",
    ]

    def __init__(self):
        self.path = Path(__file__).resolve().parent / "secrets" / ".env"
        self.env = dict(dotenv.dotenv_values(self.path))

        if not self.path.exists():
            print(
                f"Warning: {self.path} does not exist, make sure to read: https://github.com/blokkaDev/cluster/blob/main/README.md"
            )

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

    def _validate(self, required_vars, port_var):
        errors = []
        missing = [key for key in required_vars if not self.env.get(key)]

        for key in missing:
            errors.append(f"Missing required variable: {key}")

        if port_var not in missing:
            port_value = self.env.get(port_var)
            try:
                port = int(port_value)
                if not (1 <= port <= 65535):
                    raise ValueError
            except (TypeError, ValueError):
                errors.append(
                    f"Invalid value for {port_var}: '{port_value}' "
                    "(must be a valid port number between 1 and 65535)"
                )

        if errors:
            details = "\n".join(errors)
            print(
                f"✗ Invalid ACS configuration.\n\n{details}\n\n"
                f"Please check:\n{self.path}"
            )
            sys.exit(1)

    def validate_manager(self):
        self._validate(self.REQUIRED_MANAGER_VARS, "MANAGER_PORT")

    def validate_worker(self):
        self._validate(self.REQUIRED_WORKER_VARS, "WORKER_PORT")