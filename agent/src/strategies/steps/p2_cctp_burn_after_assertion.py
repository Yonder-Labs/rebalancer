from helpers import Assert
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class CctpBurnAfterAssertion(Step):
    NAME = StepName.CctpBurnAfterAssertion

    async def run(self, ctx: StrategyContext):
        # Step 4: Assert balance is (balance before - fees)
        Assert.usdc_agent_balance(ctx.web3_source, ctx.usdc_token_address_on_source_chain, expected_balance=ctx.usdc_agent_balance_before_rebalance - (ctx.cctp_fees or 0))

        print("✅ Assertion after CCTP burn passed.")