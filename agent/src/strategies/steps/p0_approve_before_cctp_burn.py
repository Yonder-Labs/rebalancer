from helpers import broadcast
from adapters import USDC
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class ApproveBeforeCctpBurnIfRequired(Step):
    NAME = StepName.ApproveBeforeCctpBurnIfRequired

    async def run(self, ctx: StrategyContext):
        # @dev since this action can only happen in the source chain, we use the messenger address there
        spender = ctx.messenger_address_on_source_chain # the messenger contract is the spender
        usdc_address = ctx.usdc_token_address_on_source_chain
        allowance = USDC.get_allowance(web3_instance=ctx.web3_source, usdc_address=usdc_address, spender=spender, owner=ctx.agent_address)
      
        print(f"Current allowance for CCTP burn on chainId={ctx.from_chain_id} is {allowance}")

        if ctx.amount > allowance:
            print("Approving USDC for CCTP burn...")
            payload = await ctx.rebalancer_contract.build_and_sign_cctp_approve_burn_tx(
                source_chain=ctx.from_chain_id,
                amount=ctx.max_allowance,
                spender=spender,
                to=usdc_address
            )

            broadcast(ctx.web3_source, payload)

            print("✅ USDC approved for CCTP burn successfully.")
            print(f"✅ Approved {ctx.max_allowance} of token {usdc_address} to spender {spender} on chainId={ctx.from_chain_id}")
        else:
            print("✅ USDC already approved for CCTP burn; no action needed.")
