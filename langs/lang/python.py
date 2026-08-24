from langchain_sandbox import PyodideSandbox

class Sandbox:
    def __init__(self):
        self.__sandbox = PyodideSandbox(
            allow_net=True
        )

    async def execute(self, code):
        return await self.__sandbox.execute(code)

    