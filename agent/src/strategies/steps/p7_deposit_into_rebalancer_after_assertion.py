from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class DepositIntoRebalancerAfterAssertion(Step):
    NAME = StepName.DepositIntoRebalancerAfterAssertion

    async def run(self, ctx: StrategyContext):
        print("Depositing into rebalancer after assertion")
        # TODO: Implement logic to deposit to rebalancer after assertion
        pass