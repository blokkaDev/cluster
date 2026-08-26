# from main import ManagerJson
import json
import socket
import sqlite3
import urllib
from importlib.resources import files
from urllib import error, request

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from zeroconf import Zeroconf

from data.env import Env
from data.sqlite import Database

app = FastAPI()
zeroconf = Zeroconf()
env = Env()
db = Database()

env.get_all()
ManagerJson = env.ManagerJson

i = 0
workers = {}
for (
    worker
) in db.get_workers():  # name, status, port, host, token, hostname, state_hostname
    try:
        workers[worker[1]] = {
            "acs_hostname": worker[6],
            "ip": worker[4],
            "port": worker[3],
        }

        data = json.dumps(
            {
                "token": worker[4],
                "hostname": worker[5],
                "manager_token": ManagerJson.get("token", None),
                "manager_hostname": socket.gethostname(),
            }
        ).encode("utf-8")

        req = request.Request(
            f"http://{worker[4]}:{worker[3]}/connect/{worker[1]}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        main_resp = request.urlopen(req)
        main_body = json.loads(main_resp.read().decode("utf-8"))

        i += 1
        print(f"Worker {worker[1]} connected [{i}/{len(db.get_workers())}]")
    except urllib.error.URLError as e:
        print(
            f"Failed to connect worker {worker[1]}: {e} [{i}/{len(db.get_workers())}]"
        )


class ConnectRequest(BaseModel):
    token: str
    remember: bool = True
    port: str = "8000"
    ip: str
    manager_token: str


class ExecuteConnectRequest(BaseModel):
    token: str
    remember: bool = True
    port: str = "8000"
    host: str
    manager_token: str
    language: str
    code: str
    return_ip: str
    return_port: str


class LoadRequest(BaseModel):
    token: str
    manager_token: str


DATA_DIR = files("data")


# def ImportJsonData(path: str = "manager.json") -> dict:
#     with open(file=DATA_DIR / path, mode="r") as file:
#         return json.load(file)


# ManagerJson = ImportJsonData()


class Manager:
    token: str = ManagerJson.get("token", None)


@app.post("/load/{worker_id}")
def load(worker_id: str, body: LoadRequest):
    if body.manager_token != Manager.token:
        return {"error": "Invalid Manager token"}

    service_name = f"acs-worker-{worker_id}._http._tcp.local."
    try:
        info = zeroconf.get_service_info(
            "_http._tcp.local.", service_name, timeout=5000
        )

        if info is None:
            return {
                "msg": "Worker not found via mDNS",
                "worker_id": worker_id,
                "service": service_name,
            }

        addresses = info.parsed_addresses()
        if not addresses:
            return {
                "msg": "Worker found but has no IP address",
                "service": service_name,
            }

        return {
            "hostname": info.server,
            "ip": addresses[0],
            "port": info.port,
            "service": service_name,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()

        return {
            "msg": "Error loading worker",
            "error": repr(e),
            "type": type(e).__name__,
        }


@app.post("/connect/{worker_id}")
def connect(worker_id: str, body: ConnectRequest):
    if body.manager_token != Manager.token:
        return {"error": "Invalid manager token"}

    hostname = f"acs.worker-{worker_id}.local"

    data = json.dumps(
        {
            "token": body.token,
            "hostname": hostname,
            "manager_token": Manager.token,
            "manager_hostname": socket.gethostname(),
        }
    ).encode("utf-8")

    # ip= socket.gethostbyname(hostname)
    try:
        req = request.Request(
            f"http://{body.ip}:{body.port}/connect/{worker_id}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        main_resp = request.urlopen(req)
        main_body = json.loads(main_resp.read().decode("utf-8"))
        sec_resp = {}

        try:
            req = request.Request(
                f"http://{body.ip}:{body.port}/connect/{worker_id}",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            main_resp = request.urlopen(req)
            main_body = json.loads(main_resp.read().decode("utf-8"))
            sec_resp = {}

            try:
                redirect = main_body.get("redirect", None)
            except Exception as e:
                redirect = None
                sec_resp = {"error": e, "page": None}

            if redirect:
                try:
                    redirect_data = json.dumps(redirect.get("data", {})).encode("utf-8")

                    req = request.Request(
                        f"http://{redirect.get('ip', '127.0.0.1')}:{redirect.get('port', '8000')}{redirect.get('page', '/')}",
                        data=redirect_data,
                        headers={"Content-Type": "application/json"},
                        method=redirect.get("method", "POST"),
                    )

                    sec_resp = request.urlopen(req)
                except (error.HTTPError, error.URLError) as e:
                    sec_resp = {
                        "error": e,
                        "page": f"http://{redirect.get('ip', '127.0.0.1')}:{redirect.get('port', '8000')}{redirect.get('page', '/')}",
                    }

        except (error.HTTPError, error.URLError) as e:
            return {
                "error": e,
                "page": f"http://{body.ip}:{body.port}/connect/{worker_id}",
            }

        try:
            redirect_body = json.loads(sec_resp.read().decode("utf-8"))
        except (UnboundLocalError, AttributeError):
            redirect_body = sec_resp

        workers[worker_id] = {
            "acs_hostname": redirect_body.get("state", {}).get("hostname", None),
            "ip": body.ip,
            "port": body.port,
            "hostname": redirect_body.get("hostname", None),
        }

        try:
            db.add_worker(
                worker_id,
                "connected",
                body.port,
                body.ip,
                body.token,
                redirect_body.get("hostname", None),
                redirect_body.get("state", {}).get("hostname", None),
            )
        except sqlite3.IntegrityError as e:
            pass

        return {"response": main_body, "redirect": redirect_body}
    except Exception as e:
        return {"error": str(e)}


@app.post("/execute/{worker_id}")
def execute(worker_id: str, body: ExecuteConnectRequest):
    if body.manager_token == Manager.token:
        hostname = f"acs.worker-{worker_id}.local"

        data = json.dumps(
            {
                "token": body.token,
                "hostname": hostname,
                "manager_token": Manager.token,
                "manager_hostname": socket.gethostname(),
                "language": body.language,
                "code": body.code,
                "return_ip": body.return_ip,
                "return_port": body.return_port,
                "ip": body.host,
                "port": body.port,
            }
        ).encode("utf-8")

        # ip= socket.gethostbyname(hostname)
        try:
            req = request.Request(
                f"http://{body.host}:{body.port}/run/code/{worker_id}",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            return json.loads(request.urlopen(req).read().decode("utf-8"))
        except (error.HTTPError, error.URLError) as e:
            return {
                "error": e,
                "page": f"http://{body.host}:{body.port}/run/code/{worker_id}",
            }


# curl -X POST http://localhost:8000 \
# -H "Content-Type: application/json" \
# -d '{"token":"3geyegyded8wgfyiuwh","remember":True, "port": "8000"}'

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
