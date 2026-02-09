from typing import Any, Dict

from near_omni_client.json_rpc.client import NearClient
from near_omni_client.wallets.near_wallet import NearWallet
from near_omni_client.providers.interfaces import IProviderFactory
from config import Config
from helpers import GasEstimator

# @dev Note: This is a base class for rebalancer actions only used for static typing purposes.
class _RebalancerBase:
    near_client: NearClient
    near_wallet: NearWallet
    near_contract_id: str
    agent_address: str
    gas_estimator: GasEstimator
    evm_provider: IProviderFactory
    config: Config

    async def _sign_and_submit_transaction(self, *, method: str, args: Dict[str, Any], gas: int, deposit: int, max_retries: int = 3, delay: float = 2.0):
        ...