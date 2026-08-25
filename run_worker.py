import machines.worker as worker

worker.uvicorn.run(
	worker.app,
	port="8000",
	host="0.0.0.0"
)
