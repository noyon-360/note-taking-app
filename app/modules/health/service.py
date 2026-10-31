class HealthService:
    def __init__(self):
        pass

    async def get_status(self) -> dict:
        return "Health is checking"