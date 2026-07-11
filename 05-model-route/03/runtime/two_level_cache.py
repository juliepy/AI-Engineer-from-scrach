class TwoLevelCache:
    def __init__(self):
        self.l1 = {}
        self.redis = None  # 接入 redis.asyncio
        self._l2_mock: dict[str, str] = {}  # 演示用 L2；生产删除，改走 redis

    async def get(self, key: str):
        if key in self.l1:
            return self.l1[key]
        # val = await self.redis.get(key)
        val = self._l2_mock.get(key) if self.redis is None else None
        if val is not None:
            self.l1[key] = val
        return val

    async def set(self, key: str, value: str, ttl: int = 300):
        self.l1[key] = value
        # await self.redis.setex(key, ttl, value)
        if self.redis is None:
            self._l2_mock[key] = value
