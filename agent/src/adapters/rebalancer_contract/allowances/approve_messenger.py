import ast

from helpers.evm_transaction import create_partial_tx

from utils import  extract_signed_rlp_without_prefix, from_chain_id_to_network
from ..common import _RebalancerBase, TGAS

class ApproveMessengerCctp(_RebalancerBase):
    async def build_cctp_approve_burn_tx(self, amount: int, spender: str):
        print(f"Building build_cctp_approve_burn tx")
        args = {
            "amount": amount,
            "spender": spender,
        }

        response = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="build_cctp_approve_burn_tx",
            args=args
        )
        print("Created build_cctp_approve_burn payload")
        raw = response.result
        as_str = bytes(raw).decode("utf-8")
        int_list = ast.literal_eval(as_str)
        payload_bytes = bytes(int_list)
        
        return payload_bytes

    async def build_and_sign_cctp_approve_burn_tx(self, source_chain: int, amount: int, spender: str,to: str):
        source_chain_as_network = from_chain_id_to_network(source_chain)
        input_payload = await self.build_cctp_approve_burn_tx(amount=amount, spender=spender)
        gas_limit = self.gas_estimator.estimate_gas_limit(source_chain_as_network, self.agent_address, to, input_payload)
        print(f"Estimated gas limit: {gas_limit}")
        
        args = {
            "args": {
                "amount": amount,
                "chain_id": source_chain,
                "partial_transaction": create_partial_tx(source_chain_as_network, self.agent_address, self.evm_provider, self.gas_estimator, gas_limit).to_dict()
            },
            "callback_gas_tgas": self.config.callback_gas_tgas
        }
        
        result = await self._sign_and_submit_transaction(
            method="build_and_sign_cctp_approve_burn_tx",
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )
        
        print(f"Received result from build_and_sign_cctp_approve_burn_tx call {result}")

        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("build_and_sign_cctp_approve_burn_tx didn't return SuccessValue")

        signed_rlp = extract_signed_rlp_without_prefix(success_value_b64)
                
        return signed_rlp

   