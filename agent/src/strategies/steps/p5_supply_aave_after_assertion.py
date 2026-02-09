from helpers import Assert
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class SupplyAaveAfterAssertion(Step):
    NAME = StepName.SupplyAaveAfterAssertion

    async def run(self, ctx: StrategyContext) -> None:
        Assert.atoken_agent_balance(
            ctx.web3_destination, 
            ctx.a_token_address_on_destination_chain,
            ctx.a_usdc_agent_balance_before_in_dest_chain + ctx.amount
        )

        print("✅ AToken balance assertion after Aave supply passed successfully.")