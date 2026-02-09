from engine_types.tx_type import TxType
from helpers import broadcast, CrossChainATokenBalanceHelper

from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName

class DepositIntoRebalancer(Step):
    NAME = StepName.DepositIntoRebalancer

    PAYLOAD_TYPE: TxType = TxType.RebalancerDeposit
    
    CAN_BE_RESTARTED = True
    
    async def run(self, ctx: StrategyContext):
        print("Depositing into rebalancer...")

        if ctx.is_restart:
            payload = await ctx.rebalancer_contract.get_signed_payload(self.PAYLOAD_TYPE)
        
            if payload:
                print("Found existing signed payload for RebalancerDeposit.")
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
        
        print("No existing signed payload for RebalancerDeposit found")
        
        crosschain_balance = CrossChainATokenBalanceHelper.get_total_cross_chain_balance()
        
        print(f"Cross-chain AToken balance: {crosschain_balance}")
        
        deposit_payload = await ctx.rebalancer_contract.build_and_sign_return_funds_tx(to_chain_id=ctx.to_chain_id, cross_chain_a_token_balance=crosschain_balance,  amount=ctx.amount, to=ctx.vault_address)

        broadcast(ctx.web3_destination, deposit_payload)

        print("Deposit transaction broadcasted successfully!")