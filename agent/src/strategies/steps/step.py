
from abc import ABC, abstractmethod
from engine_types import TxType
from ..strategy_context import StrategyContext


class Step(ABC):
    NAME: str
    PAYLOAD_TYPE: TxType
    CAN_BE_RESTARTED: bool = False
    MODIFIES_CHAIN: bool = False
    SHOULD_BE_RETRIED: bool = True
    @abstractmethod
    async def run(self, ctx: StrategyContext) -> None:
        ...