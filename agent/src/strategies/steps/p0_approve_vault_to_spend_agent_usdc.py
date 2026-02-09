from helpers import broadcast
from adapters import USDC
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class ApproveVaultToSpendAgentUSDCIfRequired(Step):
    NAME = StepName.ApproveVaultToSpendAgentUSDCIfRequired

    async def run(self, ctx: StrategyContext) -> None:
        spender = ctx.vault_address
        usdc_address = ctx.usdc_token_address_on_destination_chain

        # @dev this can only happen when the agent is returning funds to the source chain, in this case the source chain is the destination chain
        allowance = USDC.get_allowance(web3_instance=ctx.web3_destination, usdc_address=usdc_address, spender=spender, owner=ctx.agent_address)
        
        if allowance < ctx.max_allowance:
            print("Approving USDC for vault...")
            payload = await ctx.rebalancer_contract.build_and_sign_approve_vault_to_manage_agents_usdc_tx(
                to_chain_id=ctx.to_chain_id,
                to=usdc_address,
                spender=spender
            )

            broadcast(ctx.web3_destination, payload)

            print("✅ USDC approved for vault successfully.")
        else:
            print("✅ USDC already approved for vault; no action needed.")