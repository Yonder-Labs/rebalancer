from engine_types import Flow
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName


class StartRebalance(Step):
    NAME = StepName.StartRebalance

    CAN_BE_RESTARTED = False
    
    async def run(self, ctx: StrategyContext) -> None:
        print("🚀 Starting rebalance...")
        if ctx.usdc_agent_balance_before_rebalance is None:
            raise ValueError("usdc_agent_balance_before_rebalance must be set before starting rebalance.")
        
        ctx.nonce = await ctx.rebalancer_contract.start_rebalance(
            flow=ctx.flow,
            source_chain=ctx.from_chain_id,
            destination_chain=ctx.to_chain_id,
            expected_amount=ctx.amount,
            usdc_agent_balance_before=ctx.usdc_agent_balance_before_rebalance
        )
        print(f"🚀 Started rebalance with nonce: {ctx.nonce}")
