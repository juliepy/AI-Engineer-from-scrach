from dataclasses import dataclass
from typing import Literal


Env = Literal["blue", "green"]


@dataclass
class BlueGreenRouter:
    active: Env = "blue"

    def route(self) -> Env:
        return self.active

    def switch(self, target: Env) -> None:
        self.active = target

    @staticmethod
    def describe() -> str:
        return (
            "蓝绿：两套完整环境整包切换，回滚快；"
            "适合大版本/配置整体变更，代价是双倍资源。"
        )
