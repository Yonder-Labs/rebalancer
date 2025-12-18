from ..common import _RebalancerBase, TGAS
import base64


class CompleteRebalance(_RebalancerBase):
    async def complete_rebalance(self) -> int:        
        args = {}

        result = await self._sign_and_submit_transaction(
            method="complete_rebalance",
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )

        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("complete_rebalance didn't return SuccessValue")

        nonce = int(base64.b64decode(success_value_b64).decode())
        print(f"✅ nonce = {nonce}")
        
        return nonce