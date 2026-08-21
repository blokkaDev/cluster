from fastapi import FastAPI
from urllib import request, error
from pydantic import BaseModel
import socket
import uvicorn
import json
from zeroconf import Zeroconf, ServiceInfo

app = FastAPI()
zeroconf = Zeroconf()

workers = {}

class ConnectRequest(BaseModel):
    token: str
    remember: bool = True
    port: str = "8000"
    ip: str = "127.0.0.1"
    manager_token: str

class LoadRequest(BaseModel):
    token: str
    manager_token: str

def ImportJsonData(path: str="data/manager.json") -> dict:
    with open(file=path, mode="r") as file:
        return json.load(file)

ManagerJson = ImportJsonData()

class Manager:
   token: str = ManagerJson.get("token", None)

@app.post("/load/{worker_id}")
def load(worker_id: str, body: LoadRequest):
    if body.manager_token== Manager.token:
        hostname = workers.get(worker_id, {}).get("acs_hostname", f"acs-worker-{worker_id}._http._tcp.local.")

        if not hostname:
            hostname = f"acs-worker-{worker_id}._http._tcp.local."

        try:
            ip = socket.gethostbyname(str(hostname))
        except:
            ip = "127.0.0.1"
        return {
            "hostname": hostname,
            "ip": ip
        }
    else:
        return {
            "error": "Invalid Manager"
        }


@app.post("/connect/{worker_id}")
def connect(worker_id: str, body: ConnectRequest):
    if body.manager_token== Manager.token:
        hostname = f"acs.worker-{worker_id}.local"

        data = json.dumps({
            "token": body.token,
            "hostname": hostname,
            "manager_token": Manager.token,
            "manager_hostname": socket.gethostname()
        }).encode("utf-8")

        #ip= socket.gethostbyname(hostname)
        try:
            req = request.Request(
                f"http://{body.ip}:{body.port}/connect/{worker_id}",
                data=data,
                headers={
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            main_resp = request.urlopen(req)
            main_body = json.loads(main_resp.read().decode("utf-8"))
            sec_resp = {}

            try:
                redirect = main_body.get("redirect", None)
            except Exception as e:
                redirect = None
                sec_resp = {
                    "error": e,
                    "page": None
                }

            if redirect:
                try:
                    redirect_data = json.dumps(redirect.get("data", {})).encode("utf-8")

                    req = request.Request(
                        f"http://{redirect.get('ip', '127.0.0.1')}:{redirect.get('port', '8000')}{redirect.get('page', '/')}",
                        data=redirect_data,
                        headers={
                            "Content-Type": "application/json"
                        },
                        method=redirect.get("method", "POST")
                    )

                    sec_resp = request.urlopen(req)
                except error.HTTPError as e:
                    sec_resp= {
                        "error": e,
                        "page": f"http://{redirect.get("ip", "127.0.0.1")}:{redirect.get("port", "8000")}{redirect.get("page", "/")}"
                    }
            
        except error.HTTPError as e:
            return {
                "error": e,
                "page": f"http://{body.ip}:{body.port}/connect/{worker_id}"
            }
        

        try:
            redirect_body = json.loads(sec_resp.read().decode("utf-8"))
        except (UnboundLocalError, AttributeError):
            redirect_body = sec_resp

        workers[worker_id]= {
            "acs_hostname": redirect_body.get("state", {}).get("hostname", None),
            "ip": body.ip,
            "port": body.port,
            "hostname": redirect_body.get("hostname", None)
        }

        return {
            "response": main_body, 
            "redirect": redirect_body
        }
    else:
        return {
            "error": "Invalid Manager"
        }

#curl -X POST http://localhost:8000 \
# -H "Content-Type: application/json" \
# -d '{"token":"3geyegyded8wgfyiuwh","remember":True, "port": "8000"}'

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)