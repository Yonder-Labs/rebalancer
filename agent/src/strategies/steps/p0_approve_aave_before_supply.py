from helpers import broadcast
from adapters import USDC
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class ApproveAaveUSDCBeforeSupplyIfRequired(Step):
    NAME = StepName.ApproveAaveUSDCBeforeSupplyIfRequired

    async def run(self, ctx: StrategyContext) -> None:
        # @dev since this action can only happen directly in the destination chain, we use the lending pool address there.
        spender = ctx.aave_lending_pool_address_on_destination_chain
        amount = ctx.max_allowance
        allowance = USDC.get_allowance(web3_instance=ctx.web3_destination, usdc_address=ctx.usdc_token_address_on_destination_chain, spender=spender, owner=ctx.agent_address)

        if allowance < amount:
            print("Approving USDC for Aave supply...")
            payload = await ctx.rebalancer_contract.build_and_sign_aave_approve_supply_tx(
                to_chain_id=ctx.to_chain_id,
                amount=amount,
                spender=spender,
                to=ctx.usdc_token_address_on_destination_chain
            )

            broadcast(ctx.web3_destination, payload)

            print("✅ USDC approved for Aave supply successfully.")
        else:
            print("✅ USDC already approved for Aave supply; no action needed.")