import ast

from utils import from_chain_id_to_network, extract_signed_rlp
from helpers.evm_transaction import create_partial_tx

from ..common import _RebalancerBase, TGAS


class AaveWithdraw(_RebalancerBase):
    async def build_aave_withdraw_tx(self, asset: str, amount: int, on_behalf_of: str):
            print("Building aave_withdraw tx")
            args = {
                "asset": asset,
                "amount": amount,
                "on_behalf_of": on_behalf_of
            }

            response = await self.near_client.call_contract(
                contract_id=self.near_contract_id,
                method="build_aave_withdraw_tx",
                args=args
            )
            raw = response.result
            as_str = bytes(raw).decode("utf-8")
            int_list = ast.literal_eval(as_str)
            payload_bytes = bytes(int_list)
            return payload_bytes
    
    async def build_and_sign_aave_withdraw_tx(self, chain_id: int, asset: str, amount: int, on_behalf_of: str, to: str):
        chain_network = from_chain_id_to_network(chain_id)
        input_payload = await self.build_aave_withdraw_tx(asset, amount, on_behalf_of)
        gas_limit = self.gas_estimator.estimate_gas_limit(chain_network, self.agent_address, to, input_payload)
        print(f"⏳ Estimated gas limit for withdraw aave transaction: {gas_limit}")

        args = {
            "args": {
                "amount": amount,
                "partial_transaction": create_partial_tx(chain_network, self.agent_address, self.evm_provider, self.gas_estimator, gas_limit).to_dict()
            },
            "callback_gas_tgas": self.config.callback_gas_tgas
        }
        
        result = await self._sign_and_submit_transaction(
            method="build_and_sign_aave_withdraw_tx", 
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )
        print(f"Received result from build_and_sign_aave_withdraw_tx call {result}")

        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("build_and_sign_aave_withdraw_tx didn't return SuccessValue")

        signed_rlp = extract_signed_rlp(success_value_b64)
                
        return signed_rlp

