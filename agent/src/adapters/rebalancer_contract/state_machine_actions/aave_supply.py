import ast

from utils import from_chain_id_to_network, extract_signed_rlp
from helpers.evm_transaction import create_partial_tx

from ..common import _RebalancerBase, TGAS


class AaveSupply(_RebalancerBase):
    async def build_aave_supply_tx(self, asset: str, amount: int, on_behalf_of: str, referral_code: int):
        print("Building aave_deposit tx")
        args = {
            "asset": asset,
            "amount": amount,
            "on_behalf_of": on_behalf_of,
            "referral_code": referral_code
        }

        response = await self.near_client.call_contract(
            contract_id=self.near_contract_id,
            method="build_aave_supply_tx",
            args=args
        )
        raw = response.result
        as_str = bytes(raw).decode("utf-8")
        int_list = ast.literal_eval(as_str)
        payload_bytes = bytes(int_list)
        return payload_bytes
    
    async def build_and_sign_aave_supply_tx(self, to_chain_id: int, asset: str, amount: int, on_behalf_of: str,referral_code: int, to:str):
        destination_chain_as_network = from_chain_id_to_network(to_chain_id)
        input_payload = await self.build_aave_supply_tx(asset, amount, on_behalf_of, referral_code)
        gas_limit = self.gas_estimator.estimate_gas_limit(destination_chain_as_network, self.agent_address, to, input_payload)
        print(f"⏳ Estimated gas limit for supply aave transaction: {gas_limit}")

        args = {
            "args": {
                "amount": amount,
                "partial_transaction": create_partial_tx(destination_chain_as_network, self.agent_address, self.evm_provider, self.gas_estimator, gas_limit).to_dict()
            },
            "callback_gas_tgas": self.config.callback_gas_tgas
        }
        
        result = await self._sign_and_submit_transaction(
            method="build_and_sign_aave_supply_tx", 
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )

        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("build_and_sign_aave_deposit_tx didn't return SuccessValue")

        signed_rlp = extract_signed_rlp(success_value_b64)
                
        return signed_rlp
