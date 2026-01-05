from helpers import broadcast
from engine_types import TxType
from web3.exceptions import TransactionNotFound
from ..strategy_context import StrategyContext
from .step import Step

class WithdrawFromRebalancer(Step):
    NAME = "WithdrawFromRebalancer"
    
    PAYLOAD_TYPE: TxType = TxType.RebalancerWithdrawToAllocate
    
    CAN_BE_RESTARTED = True

    async def run(self, ctx: StrategyContext) -> None:
        print(f"payload type: {self.PAYLOAD_TYPE.value}")
        payload = await ctx.rebalancer_contract.get_signed_payload(self.PAYLOAD_TYPE)

        if payload:
            print("Found existing signed payload for rebalancer withdraw.")
            signed_rlp = payload
            tx_hash = ctx.web3_source.keccak(signed_rlp)

            try:
                ctx.web3_source.eth.get_transaction(tx_hash)
                return
            except TransactionNotFound:
                broadcast(ctx.web3_source, signed_rlp)
                return
        
        print("No existing signed payload found for rebalancer withdraw.")
        # if no existing signed payload, build and sign a new one
        payload = await ctx.rebalancer_contract.build_and_sign_withdraw_for_crosschain_allocation_tx(
            source_chain=ctx.from_chain_id,
            amount=ctx.amount,
            to=ctx.vault_address
        )
        
        broadcast(ctx.web3_source, payload)

        print(f"✅ Withdrew {ctx.amount} USDC from rebalancer on chain {ctx.from_chain_id}.")