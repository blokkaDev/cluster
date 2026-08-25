import json
import socket
from importlib.resources import files

import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from zeroconf import ServiceInfo, Zeroconf

from langs import Python

app = FastAPI()
python = Python()

DATA_DIR = files("data")

def ImportJsonData(path: str="workers.json") -> dict:
    with open(file=DATA_DIR / path, mode="r") as file:
        return json.load(file)

WorkerID = ImportJsonData(path="main.json").get("worker", None)
WorkerJson = ImportJsonData()
WorkerJson = WorkerJson.get(WorkerID, WorkerJson.get("lastWorker", None))

ManagerJson = ImportJsonData(path="manager.json")

class Worker:
    token: str = WorkerJson.get("token", None)
    id: str = WorkerID
    port: int = WorkerJson.get("port", None)
    hostname: str = f"acs.worker-{id}.local"
    ip: str = socket.gethostbyname(socket.gethostname())
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
        addresses=[socket.inet_aton(socket.gethostbyname(socket.gethostname()))],
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
    if Manager.connected and worker_id == Worker.id:
        if body.token == Worker.token and body.manager_token == Manager.token:
            if body.manager_hostname == Manager.hostname:
                return True
    return False

@app.post("/set/hostname/{worker_id}/{new_hostname}")
def set_hostname(worker_id: str, new_hostname: str, body: ConnectManagerRequest):
    if CheckConnectionStatus(body, worker_id):
        Worker.hostname = new_hostname
        state= UpdateWorkerHostname()

        return {
            "hostname": socket.gethostname(),
            "state": state
        }
    else:
        return {"error": "Invalid Data provided!"}

@app.post("/get/hostname")
def get_hostname(body: ConnectRequest):
    if body.token == Worker.token:
        return {"hostname": socket.gethostname()}
    else:
        return {"error": "Invalid token"}

@app.post("/load/{worker_id}")
def load_worker(worker_id: str, body: ConnectManagerRequest):
    pass

@app.post("/run/code/{worker_id}")
async def execute_code(worker_id: str, body: CodeRunnerRequest, request: Request):
    if CheckConnectionStatus(body, worker_id):
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
                "execution_time": result.execution_time
            }
        }

        #return {"requester_ip": requester_ip, "return": {"ip": return_ip, "port": return_port}} I'm gonna add this when I'll add the task chains
    else:
        return {"error": "Invalid Data provided!", "recived": body}

@app.post("/connect/{worker_id}")
def connect_manager(worker_id: str, body: ConnectManagerRequest, request: Request):
    if body.token == Worker.token:
        if not body.manager_token and not body.manager_hostname:
            return {"error": "Workers can only connect with Managers"}

        if Manager.connected and Manager.token== body.manager_token and Manager.hostname== body.manager_hostname:
            return {"error": f"Manager: {body.manager_hostname} is already connected to worker: acs.worker-{worker_id}.local"}

        if Manager.connected:
            return {"error": f"Worker: acs.worker-{worker_id}.local is already connected to an other Manager"}

        try:
            Manager.token = body.manager_token
            Manager.hostname = body.manager_hostname
            Manager.connected = True
            Manager.remember = body.remember
        except Exception as e:
            return {"error": f"Error connecting Manager, Err: {e}"}

        return {
            "redirect": {
                "ip": socket.gethostbyname(socket.gethostname()),
                "hostname": socket.gethostname(),
                "port": Worker.port,
                "page": f"/set/hostname/{worker_id}/acs.worker-{worker_id}._http._tcp.local.",
                "data": {
                    "token": body.token,
                    "hostname": body.hostname,
                    "manager_token": body.manager_token,
                    "manager_hostname": body.manager_hostname,
                    "remember": body.remember
                },
                "method": "POST"
            },
            "requester": {
                "ip": request.client.host,
                "hostname": body.manager_hostname
            }
        }
    else:
        return {"error": "Invalid token"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
