from eth_typing import ChecksumAddress
from web3 import Web3

from near_omni_client.providers.evm import AlchemyFactoryProvider

from adapters import LendingPool
from utils import from_chain_id_to_network

ATOKEN_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]


class CrossChainATokenBalanceHelper:
    _configured: bool = False

    _agent: ChecksumAddress
    _source_chain_id: int
    _evm_factory_provider: AlchemyFactoryProvider

    # chain_id -> aToken address (ONLY non-source chains)
    _a_token_by_chain: dict[int, ChecksumAddress] = {}

    @classmethod
    def configure(
        cls,
        *,
        agent_address: str,
        source_chain_id: int,
        supported_chains: list[int],
        remote_configs: dict[int, dict],
        evm_factory_provider: AlchemyFactoryProvider,
    ) -> None:
        cls._agent = Web3.to_checksum_address(agent_address)
        cls._source_chain_id = source_chain_id
        cls._a_token_by_chain = {}
        cls._evm_factory_provider = evm_factory_provider

        for chain_id in supported_chains:
            if chain_id == source_chain_id:
                continue  # 👈 agent doesn't hold aTokens on source chain

            network_id = from_chain_id_to_network(chain_id)
            web3 = evm_factory_provider.get_provider(network_id)

            lending_pool = remote_configs[chain_id]["aave"]["lending_pool_address"]
            usdc = remote_configs[chain_id]["aave"]["asset"]

            a_token_address = LendingPool.get_atoken_address(
                web3_instance=web3,
                lending_pool_address=lending_pool,
                asset_address=usdc,
            )
            if not a_token_address:
                raise ValueError(f"Failed to resolve aToken for chain_id={chain_id}")

            cls._a_token_by_chain[chain_id] = Web3.to_checksum_address(a_token_address)

        cls._configured = True

    @classmethod
    def _ensure(cls) -> None:
        if not cls._configured:
            raise RuntimeError("CrossChainATokenBalanceHelper not configured")

    @classmethod
    def get_total_cross_chain_balance(cls) -> int:
        """
        Sums aToken balances of AGENT across all NON-source chains.
        """
        cls._ensure()

        total = 0

        for chain_id, a_token in cls._a_token_by_chain.items():
            network_id = from_chain_id_to_network(chain_id)
            web3 = cls._evm_factory_provider.get_provider(network_id)

            balance = (
                web3.eth.contract(address=a_token, abi=ATOKEN_ABI)
                .functions.balanceOf(cls._agent)
                .call()
            )

            total += balance

        return total