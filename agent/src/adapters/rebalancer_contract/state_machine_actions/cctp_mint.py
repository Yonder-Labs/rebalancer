import ast

from utils import from_chain_id_to_network, extract_signed_rlp, hex_to_int_list
from helpers.evm_transaction import create_partial_tx

from ..common import _RebalancerBase, TGAS


class CctpMint(_RebalancerBase):    
    async def build_cctp_mint_tx(self, message: str, attestation: str):
        print("Building cctp_mint tx")
        args = {
            "message": hex_to_int_list(message),
            "attestation": hex_to_int_list(attestation)
        }

        response = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="build_cctp_mint_tx",
            args=args
        )
        print("Created cctp_mint payload")
        raw = response.result
        as_str = bytes(raw).decode("utf-8")
        int_list = ast.literal_eval(as_str)
        payload_bytes = bytes(int_list)
        return payload_bytes
    
    async def build_and_sign_cctp_mint_tx(self, to_chain_id: int, message: str, attestation: str, to: str): 
        print("Building and signing cctp_mint tx")
        print(f"chain id: {to_chain_id}")
        destination_chain_as_network = from_chain_id_to_network(to_chain_id)
        input_payload = await self.build_cctp_mint_tx(message, attestation)
        gas_limit = self.gas_estimator.estimate_gas_limit(destination_chain_as_network, self.agent_address, to, input_payload)
        print(f"⏳ Estimated gas limit: {gas_limit}")
       
        args = {
            "args": {
                "message": hex_to_int_list(message),
                "attestation": hex_to_int_list(attestation),
                "partial_mint_transaction": create_partial_tx(destination_chain_as_network, self.agent_address, self.evm_provider, self.gas_estimator, gas_limit=gas_limit).to_dict(), 
            },
            "callback_gas_tgas": self.config.callback_gas_tgas
        }
        
        result = await self._sign_and_submit_transaction(
            method="build_and_sign_cctp_mint_tx", 
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )
        print(f"Received result from build_and_sign_cctp_mint_tx call {result}")
        
        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("build_and_sign_cctp_mint_tx didn't return SuccessValue")

        signed_rlp = extract_signed_rlp(success_value_b64)
                
        return signed_rlp