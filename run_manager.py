from machines import manager

manager.uvicorn.run(manager.app, port=8001, host="0.0.0.0")
