import ast

from typing import Any

from utils import from_chain_id_to_network, extract_signed_rlp
from helpers.evm_transaction import create_partial_tx
from ..common import _RebalancerBase, TGAS


class WithdrawForCrossChainAllocation(_RebalancerBase):
    async def build_withdraw_for_crosschain_allocation_tx(self, amount: int, cross_chain_a_token_balance: Any = None):
        print("Building withdraw_for_crosschain_allocation tx")
        args = {
            "amount": amount,
            "cross_chain_a_token_balance": cross_chain_a_token_balance
        }

        response = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="build_withdraw_for_crosschain_allocation_tx",
            args=args
        )
        raw = response.result
        as_str = bytes(raw).decode("utf-8")
        int_list = ast.literal_eval(as_str)
        payload_bytes = bytes(int_list)
        return payload_bytes

    async def build_and_sign_withdraw_for_crosschain_allocation_tx(self, source_chain: int, amount: int, to: str):
        source_chain_as_network = from_chain_id_to_network(source_chain)
        input_payload = await self.build_withdraw_for_crosschain_allocation_tx(amount=amount)
        gas_limit = self.gas_estimator.estimate_gas_limit(source_chain_as_network, self.agent_address, to, input_payload)
        
        args = {
            "rebalancer_args": {
                "amount": amount,
                "partial_transaction": create_partial_tx(source_chain_as_network, self.agent_address, self.evm_provider, self.gas_estimator, gas_limit).to_dict(),
                "cross_chain_a_token_balance": None
            },
            "callback_gas_tgas": self.config.callback_gas_tgas
        }

        result = await self._sign_and_submit_transaction(
            method="build_and_sign_withdraw_for_crosschain_allocation_tx",
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )

        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("withdraw_for_crosschain_allocation didn't return SuccessValue")

        signed_rlp = extract_signed_rlp(success_value_b64)
                
        return signed_rlp