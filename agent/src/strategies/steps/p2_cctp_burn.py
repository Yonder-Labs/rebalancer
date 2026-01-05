from helpers import broadcast
from engine_types import TxType

from ..strategy_context import StrategyContext
from .step import Step

class CctpBurn(Step):
    NAME = "CctpBurn"

    PAYLOAD_TYPE: TxType = TxType.CCTPBurn

    CAN_BE_RESTARTED = True
    
    async def run(self, ctx: StrategyContext):
        burn_token = ctx.usdc_token_address_on_source_chain

        payload = await ctx.rebalancer_contract.get_signed_payload(self.PAYLOAD_TYPE)

        if payload:
            print("Found existing signed payload for CctpBurn.")
            signed_rlp = payload
            tx_hash = ctx.web3_source.keccak(signed_rlp)

            # Check if the transaction is already mined
            try:
                ctx.web3_source.eth.get_transaction(tx_hash)
                return
            except Exception:
                # If not found, broadcast the signed payload
                broadcast(ctx.web3_source, signed_rlp)
                ctx.burn_tx_hash = f"0x{tx_hash.hex()}"
                return

        print("No existing signed payload for CctpBurn found")

        payload = await ctx.rebalancer_contract.build_and_sign_cctp_burn_tx(
            source_chain=ctx.from_chain_id,
            to_chain_id=ctx.to_chain_id,
            amount=ctx.amount + (ctx.cctp_fees or 0),
            max_fee=ctx.cctp_fees or 0,
            burn_token=burn_token,
            to=ctx.messenger_address_on_source_chain
        )

        tx_hash = broadcast(ctx.web3_source, payload)

        print(f"✅ CctpBurn transaction broadcasted successfully!")

        ctx.burn_tx_hash = f"0x{tx_hash}"