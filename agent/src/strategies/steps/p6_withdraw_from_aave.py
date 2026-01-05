from helpers import broadcast
from engine_types import TxType

from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class WithdrawFromAave(Step):
    NAME = StepName.WithdrawFromAave
    
    PAYLOAD_TYPE: TxType = TxType.AaveWithdraw
    
    CAN_BE_RESTARTED = True
    
    async def run(self, ctx: StrategyContext) -> None:
        asset = ctx.usdc_token_address_on_source_chain
        on_behalf = ctx.agent_address

        if ctx.is_restart:
            payload = await ctx.rebalancer_contract.get_signed_payload(self.PAYLOAD_TYPE)
        
            if payload:
                print("Found existing signed payload for AaveWithdraw.")
                signed_rlp = payload
                tx_hash = ctx.web3_source.keccak(signed_rlp)
                # Check if the transaction is already mined
                try:
                    ctx.web3_source.eth.get_transaction(tx_hash)
                    return
                except Exception:
                    # If not found, broadcast the signed payload
                    broadcast(ctx.web3_source, signed_rlp)
                    return

        print("No existing signed payload for AaveWithdraw found")

        # @dev since we can only interact directly with an Aave Lending Pool contract in a NON-Source chain,
        # it means that we are trying to move funds from the NON-Source chain, therefore the chain id is the from_chain_id
        payload = await ctx.rebalancer_contract.build_and_sign_aave_withdraw_tx(
            chain_id=ctx.from_chain_id,
            asset=asset,
            amount=ctx.amount,
            on_behalf_of=on_behalf,
            to=ctx.aave_lending_pool_address_on_source_chain
        )
        broadcast(ctx.web3_source, payload)

        print("✅ Withdraw from Aave transaction broadcasted successfully!")