class Python:
    def __init__(self):
        from langs.lang.python import Sandbox
        self.__LANG = Sandbox()

    async def execute(self, code: str):
        return await self.__LANG.execute(code)