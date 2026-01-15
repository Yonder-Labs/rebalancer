import time
from helpers import broadcast
from engine_types import TxType

from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName
from .constants import POLL_INTERVAL_SECONDS

class SupplyAave(Step):
    NAME = StepName.SupplyAave

    PAYLOAD_TYPE: TxType = TxType.AaveSupply
    
    CAN_BE_RESTARTED = True
    
    async def run(self, ctx: StrategyContext) -> None:
        asset = ctx.usdc_token_address_on_destination_chain
        on_behalf = ctx.agent_address
        referral = ctx.remote_config[ctx.to_chain_id]["aave"]["referral_code"]

        if ctx.is_restart:
            supply_payload = await ctx.rebalancer_contract.get_signed_payload(self.PAYLOAD_TYPE)

            if supply_payload:
                print("Found existing signed payload for AaveSupply.")
                signed_rlp = supply_payload
                tx_hash = ctx.web3_destination.keccak(signed_rlp)

                # Check if the transaction is already mined
                try:
                    ctx.web3_destination.eth.get_transaction(tx_hash)
                    return
                except Exception:
                    # If not found, broadcast the signed payload
                    broadcast(ctx.web3_destination, signed_rlp)
                    return
            
        print("No existing signed payload for AaveSupply found")
        
        supply_payload = await ctx.rebalancer_contract.build_and_sign_aave_supply_tx(
            to_chain_id=ctx.to_chain_id,
            asset=asset,
            amount=ctx.amount,
            on_behalf_of=on_behalf,
            referral_code=referral,
            to=ctx.aave_lending_pool_address_on_destination_chain
        )

        broadcast(ctx.web3_destination, supply_payload)

        print("Aave supply transaction broadcasted successfully.")

        time.sleep(POLL_INTERVAL_SECONDS)  # Wait for a short period to ensure the transaction is processed