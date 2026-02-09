from typing import Optional
from config import Config
from adapters import RebalancerContract
from utils import from_chain_id_to_network
from engine_types import Flow

from near_omni_client.providers.evm import AlchemyFactoryProvider
from near_omni_client.adapters.cctp.attestation_service_types import Message

class StrategyContext:
    def __init__(
        self,
        *,
        from_chain_id: int,
        to_chain_id: int,
        amount: int,
        remote_config: dict,
        config: Config,
        agent_address: str,
        vault_address: str,
        evm_factory_provider: AlchemyFactoryProvider,
        rebalancer_contract: RebalancerContract,
        flow: Flow,
        max_allowance: int,
        is_restart: bool = False,
        restart_from: Optional[str] = None,
        usdc_agent_balance_before_in_source_chain: Optional[int] = None,
        usdc_agent_balance_before_in_dest_chain: Optional[int] = None,
        a_usdc_agent_balance_before_in_source_chain: Optional[int] = None,
        a_usdc_agent_balance_before_in_dest_chain: Optional[int] = None
    ):
        self.from_chain_id = from_chain_id
        self.to_chain_id = to_chain_id
        self.amount = amount
        self.flow = flow
        
        self.remote_config = remote_config
        self.config = config
        self.agent_address = agent_address
        self.vault_address = vault_address
        self.max_allowance = max_allowance
        self.evm_factory_provider = evm_factory_provider
        self.rebalancer_contract = rebalancer_contract
        
        self.from_network_id = from_chain_id_to_network(from_chain_id)
        self.to_network_id = from_chain_id_to_network(to_chain_id)
        self.web3_source = evm_factory_provider.get_provider(self.from_network_id)
        self.web3_destination = evm_factory_provider.get_provider(self.to_network_id)

        self.usdc_token_address_on_source_chain: str = self.remote_config[from_chain_id]["aave"]["asset"]
        self.usdc_token_address_on_destination_chain: str = self.remote_config[to_chain_id]["aave"]["asset"]

        self.messenger_address_on_source_chain: str = self.remote_config[from_chain_id]["cctp"]["messenger_address"]
        self.transmitter_address_on_destination_chain: str = self.remote_config[to_chain_id]["cctp"]["transmitter_address"]

        self.aave_lending_pool_address_on_destination_chain: str = self.remote_config[to_chain_id]["aave"]["lending_pool_address"]
        self.aave_lending_pool_address_on_source_chain: str = self.remote_config[from_chain_id]["aave"]["lending_pool_address"]

        self.is_restart = is_restart
        self.restart_from = restart_from
        
        # ===== filled by phases =====
        self.nonce: Optional[int] = None
        
        self.usdc_agent_balance_before_in_source_chain: Optional[int] = usdc_agent_balance_before_in_source_chain # can be set during restart
        self.usdc_agent_balance_before_in_dest_chain: Optional[int] = usdc_agent_balance_before_in_dest_chain # can be set during restart
        
        self.a_usdc_agent_balance_before_in_source_chain: Optional[int] = a_usdc_agent_balance_before_in_source_chain # can be set during restart
        self.a_usdc_agent_balance_before_in_dest_chain: Optional[int] = a_usdc_agent_balance_before_in_dest_chain # can be set during restart
        
        self.a_token_address_on_destination_chain: Optional[str] = None
        self.a_token_address_on_source_chain: Optional[str] = None

        self.cctp_fees: Optional[int] = None
        self.burn_tx_hash: Optional[str] = None
        self.attestation: Optional[Message] = None