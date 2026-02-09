from helpers.evm_transaction import create_partial_tx

from ..common import _RebalancerBase, TGAS

class RegisterWorker(_RebalancerBase):
    async def register_worker(self, quote_hex:str, collateral:str, checksum:str, tcb_info:dict):
        print("Calling register_worker")

        args = {
            "quote_hex": quote_hex,
            "collateral": collateral,
            "checksum": checksum,
            "tcb_info": tcb_info
        }
        
        result = await self._sign_and_submit_transaction(
            method="register_worker",
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )
        print(f"Received result from register_worker {result}")

        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("register_worker didn't return SuccessValue")
        

    