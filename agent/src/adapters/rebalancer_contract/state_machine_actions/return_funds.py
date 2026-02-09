import ast

from utils import from_chain_id_to_network, extract_signed_rlp
from helpers.evm_transaction import create_partial_tx

from ..common import _RebalancerBase, TGAS

class ReturnFunds(_RebalancerBase):
    async def build_return_funds_tx(self, amount: int, cross_chain_a_token_balance: int):
        print("Building return_funds tx")
        args = {
            "amount": amount,
            "cross_chain_a_token_balance": cross_chain_a_token_balance
        }

        response = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="build_return_funds_tx",
            args=args
        )
        raw = response.result
        as_str = bytes(raw).decode("utf-8")
        int_list = ast.literal_eval(as_str)
        payload_bytes = bytes(int_list)
        
        return payload_bytes

    async def build_and_sign_return_funds_tx(self, to_chain_id: int, amount: int, cross_chain_a_token_balance: int, to: str):   
        chain_as_network = from_chain_id_to_network(to_chain_id)
        input_payload = await self.build_return_funds_tx(amount=amount, cross_chain_a_token_balance=cross_chain_a_token_balance)
        gas_limit = self.gas_estimator.estimate_gas_limit(chain_as_network, self.agent_address, to, input_payload)
        print(f"⏳ Estimated gas limit: {gas_limit}")
        
        args = {
            "args": {
                "amount": amount,
                "cross_chain_a_token_balance": cross_chain_a_token_balance,
                "partial_transaction": create_partial_tx(chain_as_network, self.agent_address, self.evm_provider, self.gas_estimator, gas_limit).to_dict()
            },
            "callback_gas_tgas": self.config.callback_gas_tgas
        }
        
        result = await self._sign_and_submit_transaction(
            method="build_and_sign_return_funds_tx",
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )
        
        print(f"Received result from build_and_sign_return_funds_tx call {result}")

        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("return_funds didn't return SuccessValue")


        signed_rlp = extract_signed_rlp(success_value_b64)
                
        return signed_rlp

    