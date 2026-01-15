from helpers import BalanceHelper
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class GetUSDCBalanceBeforeDepositToRebalancer(Step):
    NAME = StepName.GetUSDCBalanceBeforeDepositToRebalancer

    async def run(self, ctx: StrategyContext):
        print("Getting USDC balance before deposit to rebalancer...")

        ctx.usdc_agent_balance_before_deposit_to_rebalancer = BalanceHelper.get_usdc_agent_balance(ctx.web3_destination, ctx.usdc_token_address_on_destination_chain)

        if ctx.usdc_agent_balance_before_deposit_to_rebalancer is None:
            raise ValueError("USDC agent balance before deposit to rebalancer is not set in context.")
        