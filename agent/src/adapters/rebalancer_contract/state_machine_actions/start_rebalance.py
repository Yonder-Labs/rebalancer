import base64

from engine_types import Flow
from ..common import _RebalancerBase, TGAS

class StartRebalance(_RebalancerBase):
     async def start_rebalance(self, flow: Flow, source_chain: int, destination_chain: int, expected_amount: int, usdc_agent_balance_before: int) -> int:        
        print(f"🚀 Starting rebalance... FLOW={flow.name}, source_chain={source_chain}, destination_chain={destination_chain}, expected_amount={expected_amount}, usdc_agent_balance_before={usdc_agent_balance_before}")
        args = {
            "flow": flow.name,
            "source_chain": source_chain,
            "destination_chain": destination_chain,
            "amount": expected_amount,
            "usdc_agent_balance_before": usdc_agent_balance_before
        }

        result = await self._sign_and_submit_transaction(
            method="start_rebalance",
            args=args,
            gas=self.config.tx_tgas * TGAS,
            deposit=0
        )

        success_value_b64 = result.status.get("SuccessValue")
        if not success_value_b64:
            raise Exception("start_rebalance didn't return SuccessValue")

        nonce = int(base64.b64decode(success_value_b64).decode())
        print(f"✅ nonce = {nonce}")
        
        return nonce