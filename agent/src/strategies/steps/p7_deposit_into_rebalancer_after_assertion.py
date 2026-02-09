from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class DepositIntoRebalancerAfterAssertion(Step):
    NAME = StepName.DepositIntoRebalancerAfterAssertion

    async def run(self, ctx: StrategyContext):
        print("Depositing into rebalancer after assertion")

        # TODO: I should assert that the balance after deposit is what I had before - deposited amount