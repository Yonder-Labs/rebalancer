import time
from helpers import broadcast
from engine_types import TxType
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName
from .constants import POLL_INTERVAL_SECONDS

class CctpMint(Step):
    NAME = StepName.CctpMint
    
    PAYLOAD_TYPE: TxType = TxType.CCTPMint
    
    CAN_BE_RESTARTED = True

    async def run(self, ctx: StrategyContext):
        if ctx.is_restart:
            payload = await ctx.rebalancer_contract.get_signed_payload(self.PAYLOAD_TYPE)

            if payload:
                print("Found existing signed payload for CctpMint.")
                signed_rlp = payload
                tx_hash = ctx.web3_destination.keccak(signed_rlp)

                # Check if the transaction is already mined
                try:
                    ctx.web3_destination.eth.get_transaction(tx_hash)
                    return
                except Exception:
                    # If not found, broadcast the signed payload
                    broadcast(ctx.web3_destination, signed_rlp)
                    return
            
        print("No existing signed payload for CctpMint found")

        payload = await ctx.rebalancer_contract.build_and_sign_cctp_mint_tx(
            to_chain_id=ctx.to_chain_id,
            message=ctx.attestation.message,
            attestation=ctx.attestation.attestation,
            to=ctx.transmitter_address_on_destination_chain
        )

        broadcast(ctx.web3_destination, payload)

        print("Mint transaction broadcasted successfully!")

        time.sleep(POLL_INTERVAL_SECONDS)