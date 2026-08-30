# import json
import socket

# from cmath import e
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from fastapi_cloud_cli.commands.env import env_app
from pydantic import BaseModel
from zeroconf import ServiceInfo, Zeroconf

# from data.sqlite import Database
from data.env import Env
from langs import Python

# from main import ManagerJson
# from main import WorkerJson

app = FastAPI()
python = Python()
# db = Database()
env = Env()
env.validate_worker()

BASE_DIR = Path(__file__).resolve().parent.parent

HTML_DIR = BASE_DIR / "HTML"

templates = Jinja2Templates(directory=str(HTML_DIR))

app.mount(
    "/static",
    StaticFiles(directory=str(HTML_DIR / "worker")),
    name="static",
)


# I'm not using this anymore
# def ImportJsonData(path: str = "workers.json") -> dict:
#    with open(file=DATA_DIR / path, mode="r") as file:
#        return json.load(file)


# WorkerID = ImportJsonData(path="main.json").get("worker", None)
# WorkerJson = ImportJsonData()
# WorkerJson = WorkerJson.get(WorkerID, WorkerJson.get("lastWorker", None))

# ManagerJson = ImportJsonData(path="manager.json")

# WorkerID = "idd-2"
# I'm not using this too (manager only)
# WorkerJson = db.select_worker_by_name(name=WorkerID)


EnvData = env.get_all()
ManagerJson = env.ManagerJson
WorkerJson = env.WorkerJson

# print("manager:", ManagerJson)
# print("worker:", WorkerJson)


def _resolve_local_ip() -> str:
    """Resolve the local machine IP, falling back to loopback if the
    hostname cannot be resolved (e.g. unusual DNS setups on FreeBSD/some
    containers)."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return "127.0.0.1"


class Worker:
    token: str = WorkerJson.get("token", None)
    id: str = WorkerJson.get("id", None)
    port: int = WorkerJson.get("port", None)
    hostname: str = f"acs.worker-{id}.local"
    ip: str = _resolve_local_ip()
    info: ServiceInfo | None = None

    record: bool = False


class Manager:
    token: str = ManagerJson.get("token", None)
    connected: bool = False
    hostname: str = ManagerJson.get("hostname", None)
    remember: bool = ManagerJson.get("remember", None)


zeroconf = Zeroconf()


def UpdateWorkerHostname() -> dict:
    hostname = Worker.hostname.rstrip(".") + "."
    service_name = "_http._tcp.local."
    info = ServiceInfo(
        service_name,
        f"acs-worker-{Worker.id}._http._tcp.local.",
        addresses=[socket.inet_aton(_resolve_local_ip())],
        port=Worker.port,
        server=hostname,
    )

    if Worker.info is None:
        zeroconf.register_service(info)
    else:
        zeroconf.update_service(info)
    Worker.info = info

    return {
        "value": True,
        "hostname": hostname,
        "ip": Worker.ip,
        "service": info.name,
    }


UpdateWorkerHostname()


class ConnectRequest(BaseModel):
    token: str


class CodeRunnerRequest(BaseModel):
    token: str
    hostname: str
    manager_token: str
    manager_hostname: str
    remember: bool = True
    language: str
    code: str
    return_ip: str
    return_port: str


class ConnectManagerRequest(BaseModel):
    token: str
    hostname: str
    manager_token: str
    manager_hostname: str
    remember: bool = True


def CheckConnectionStatus(body, worker_id):
    msg = "Invalid Data provided!"
    if not Manager.connected:
        return {"state": False, "message": "Manager not connected"}

    if not worker_id:
        return {"state": False, "message": "Invalid worker id"}

    if not body.token:
        return {"state": False, "message": "Invalid token"}

    if not body.manager_token:
        return {"state": False, "message": "Invalid manager token"}

    if not body.manager_hostname:
        return {"state": False, "message": "Invalid manager hostname"}

    if worker_id == Worker.id:
        if body.token == Worker.token and body.manager_token == Manager.token:
            if body.manager_hostname == Manager.hostname:
                return {"state": True, "message": "Connected successfully"}
            else:
                msg = f"Invalid manager hostname: {body.manager_hostname}"
        else:
            msg = "Invalid token"
    else:
        msg = f"Invalid worker id: {worker_id}"
    return {"state": False, "message": msg}


@app.post("/set/hostname/{worker_id}/{new_hostname}")
def set_hostname(worker_id: str, new_hostname: str, body: ConnectManagerRequest):
    state = CheckConnectionStatus(body, worker_id)
    if state["state"]:
        Worker.hostname = new_hostname
        state = UpdateWorkerHostname()

        return {"hostname": socket.gethostname(), "state": state}
    else:
        return {"error": state["message"]}


@app.post("/get/hostname")
def get_hostname(body: ConnectRequest):
    if body.token == Worker.token:
        return {"hostname": socket.gethostname()}
    else:
        return {"error": "Invalid token"}


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="worker/index.html",
        context={
            "worker_id": Worker.id,
        },
    )


@app.post("/get/id")
def get_id(body: ConnectRequest):
    if body.token == Worker.token:
        return {"id": Worker.id}
    else:
        return {"error": "Invalid token"}


@app.post("/load/{worker_id}")
def load_worker(worker_id: str, body: ConnectManagerRequest):
    pass


@app.post("/run/code/{worker_id}")
async def execute_code(worker_id: str, body: CodeRunnerRequest, request: Request):
    state = CheckConnectionStatus(body, worker_id)
    if state["state"]:
        # the worker will send the result to a specified machine
        requester_ip = request.client.host
        return_ip = body.return_ip
        return_port = body.return_port
        result = await python.execute(body.code)

        if result.status == "success":
            result.status = True
        else:
            result.status = False

        return {
            "result": {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": result.status,
                "execution_time": result.execution_time,
            }
        }

        # return {"requester_ip": requester_ip, "return": {"ip": return_ip, "port": return_port}} I'm gonna add this when I'll add the task chains
    else:
        return {"error": state["message"]}


@app.post("/connect/{worker_id}")
def connect_manager(worker_id: str, body: ConnectManagerRequest, request: Request):
    if body.token == Worker.token:
        if not body.manager_token and not body.manager_hostname:
            return {"error": "Workers can only connect with Managers"}

        if (
            Manager.connected
            and Manager.token == body.manager_token
            and Manager.hostname == body.manager_hostname
        ):
            return {
                "error": f"Manager: {body.manager_hostname} is already connected to worker: acs.worker-{worker_id}.local"
            }

        if Manager.connected:
            return {
                "error": f"Worker: acs.worker-{worker_id}.local is already connected to an other Manager"
            }

        try:
            Manager.token = body.manager_token
            Manager.hostname = body.manager_hostname
            Manager.connected = True
            Manager.remember = body.remember
        except Exception as e:
            return {"error": f"Error connecting Manager, Err: {e}"}

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()

        return {
            "redirect": {
                "ip": ip,
                "hostname": socket.gethostname(),
                "port": Worker.port,
                "page": f"/set/hostname/{worker_id}/acs.worker-{worker_id}._http._tcp.local.",
                "data": {
                    "token": body.token,
                    "hostname": body.hostname,
                    "manager_token": body.manager_token,
                    "manager_hostname": body.manager_hostname,
                    "remember": body.remember,
                },
                "method": "POST",
            },
            "requester": {"ip": request.client.host, "hostname": body.manager_hostname},
        }
    else:
        return {"error": "Invalid token"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
