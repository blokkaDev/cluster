import threading
import time
import uvicorn
from urllib import request
import socket
import json
 
import manager
import worker


def run_manager():
    uvicorn.run(
        manager.app,
        host="0.0.0.0",
        port=8001,
    )


def run_worker():
    uvicorn.run(
        worker.app,
        host="0.0.0.0",
        port=8000,
    )


manager_thread = threading.Thread(
    target=run_manager,
    daemon=True,
)

worker_thread = threading.Thread(
    target=run_worker,
    daemon=True,
)

manager_thread.start()
worker_thread.start()

time.sleep(1)

def ImportJsonData(path: str="data/workers.json") -> dict:
    with open(file=path, mode="r") as file:
        return json.load(file)

WorkerID = ImportJsonData(path="data/main.json").get("worker", None)
WorkerJson = ImportJsonData()
WorkerJson = WorkerJson.get(WorkerID, WorkerJson.get("lastWorker", None))

ManagerJson = ImportJsonData(path="data/manager.json")

class Worker():
    id: str = WorkerID
    token: str = WorkerJson.get("token", None)
    port: int = WorkerJson.get("port", None)
    ip: str = "127.0.0.1"

class Manager():
    token: str = ManagerJson.get("token", None)
    connected: bool = False
    hostname: str = socket.gethostname()
    remember: bool = ManagerJson.get("remember", None)
    port: int = ManagerJson.get("port", None)
    ip: str = "127.0.0.1"

def post(url, data):
    req = request.Request(
        url=url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST"
    )

    with request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result


#connect Worker.id to Manager
post(
    url=f"http://{Manager.ip}:{Manager.port}/connect/{Worker.id}",
    data={
        "token": str(Worker.token),
        "remember": str(Manager.remember),
        "manager_token": str(Manager.token),
        "ip": str(Worker.ip),
        "port": str(Worker.port)
    }
)

print(post(
    url=f"http://{Manager.ip}:{Manager.port}/load/{Worker.id}",
    data={
        "token": str(Worker.token),
        "manager_token": str(Manager.token)
    }
))





try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Closing...")
