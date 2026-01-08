
from abc import ABC, abstractmethod
from engine_types import TxType
from ..strategy_context import StrategyContext
from .step_names import StepName

class Step(ABC):
    NAME: StepName
    PAYLOAD_TYPE: TxType
    CAN_BE_RESTARTED: bool = False
    MODIFIES_CHAIN: bool = False
    SHOULD_BE_RETRIED: bool = True
    REQUIRED_STEPS: list[StepName] = []
    
    @abstractmethod
    async def run(self, ctx: StrategyContext) -> None:
        ...