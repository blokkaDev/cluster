import machines.manager as manager

manager.uvicorn.run(
	manager.app,
	port="8001",
	host="127.0.0.1"
)
