from engine_types import TxType

from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName


class CompleteRebalance(Step):
    NAME = StepName.CompleteRebalance

    PAYLOAD_TYPE: TxType = TxType.CompleteRebalance

    async def run(self, ctx: StrategyContext) -> None:
        print("Completing rebalance...")
        
        ctx.nonce = await ctx.rebalancer_contract.complete_rebalance()
        
        print(f"Completed rebalance with nonce: {ctx.nonce}")
