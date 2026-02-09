import ast

from utils import from_chain_id_to_network, extract_signed_rlp
from helpers.evm_transaction import create_partial_tx

from ..common import _RebalancerBase, TGAS


class CctpBurn(_RebalancerBase):
    async def build_cctp_burn_tx(self, destination_domain: int, amount: int, max_fee: int, burn_token: str):
        print("Building cctp_burn tx")        
        args = {
            "amount": amount,
            "destination_domain": destination_domain,
            "mint_recipient": "0x" + self.agent_address_as_bytes32.hex(),
            "burn_token": burn_token,
            "destination_caller": "0x" + self.agent_address_as_bytes32.hex(),
            "max_fee": max_fee,
            "min_finality_threshold": self.config.min_bridge_finality_threshold
        }

        response = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="build_cctp_burn_tx",
            args=args
        )
        print("Created cctp_burn payload")
        raw = response.result
        as_str = bytes(raw).decode("utf-8")
        int_list = ast.literal_eval(as_str)
        payload_bytes = bytes(int_list)
        
        return payload_bytes

    async def build_and_sign_cctp_burn_tx(self, source_chain: int, to_chain_id: int, amount: int, max_fee: int, burn_token: str, to: str):
        source_chain_as_network = from_chain_id_to_network(source_chain)
        destination_domain = int(from_chain_id_to_network(to_chain_id).domain)
        input_payload = await self.build_cctp_burn_tx(destination_domain=destination_domain, amount=amount, max_fee=max_fee, burn_token=burn_token)
        gas_limit = self.gas_estimator.estimate_gas_limit(source_chain_as_network, self.agent_address, to, input_payload)
        print(f"⏳ Estimated gas limit for burn transaction: {gas_limit}")

        args = {
            "args": {
                "amount": amount,
                "destination_domain": destination_domain,
                "mint_recipient": "0x" + self.agent_address_as_bytes32.hex(),
                "burn_token": burn_token,
                "destination_caller": "0x" + self.agent_address_as_bytes32.hex(),
                "max_fee": max_fee,
                "min_finality_threshold": self.config.min_bridge_finality_threshold,
                "partial_burn_transaction": create_partial_tx(source_chain_as_network, self.agent_address, self.evm_provider, self.gas_estimator, gas_limit).to_dict()
            },
            "callback_gas_tgas": self.config.callback_gas_tgas
        }
        
        result = await self._sign_and_submit_transaction(
            method="build_and_sign_cctp_burn_tx",
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )

        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("withdraw_for_crosschain_allocation didn't return SuccessValue")

        signed_rlp = extract_signed_rlp(success_value_b64)
                
        return signed_rlp
    
 

