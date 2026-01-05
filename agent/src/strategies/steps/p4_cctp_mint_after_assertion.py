from helpers import Assert
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class CctpMintAfterAssertion(Step):
    NAME = StepName.CctpMintAfterAssertion

    async def run(self, ctx: StrategyContext):
        Assert.usdc_agent_balance_is_at_least(ctx.web3_destination, ctx.usdc_token_address_on_destination_chain, expected_balance=ctx.amount)

        print("Balance assertion after mint passed.")