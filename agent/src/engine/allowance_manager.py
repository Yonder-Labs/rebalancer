from utils import from_chain_id_to_network
from engine import EngineContext
from adapters import USDC

async def check_and_execute_allowances(context: EngineContext, max_allowance: int):
    supported_chains = await context.rebalancer_contract.get_supported_chains()
    
    for chain_id in supported_chains:
        network_id = from_chain_id_to_network(chain_id)
        web3_instance = context.evm_factory_provider.get_provider(network_id)
        aave_lending_pool_address = context.remote_configs[chain_id]["aave"]["lending_pool_address"]
        usdc_token_address: str = context.remote_configs[chain_id]["aave"]["asset"]
        messenger_address = context.remote_configs[chain_id]["cctp"]["messenger_address"]
        messenger_allowance = USDC.get_allowance(web3_instance=web3_instance, usdc_address=usdc_token_address, spender=messenger_address)

        if messenger_allowance < max_allowance:
            # we execute tx
            pass

        if chain_id == context.source_chain_id:
            # TODO: revisar si necesito la address del owner
            vault_allowance = USDC.get_allowance(web3_instance=web3_instance, usdc_address=usdc_token_address, spender=context.vault_address)
            if vault_allowance < max_allowance:
                # here we execute the allowance
                pass     
            pass 
        else:
            lending_pool_allowance = USDC.get_allowance(web3_instance=web3_instance, usdc_address=usdc_token_address, spender=aave_lending_pool_address)
            if lending_pool_allowance < max_allowance:
                # here we execute the allowance
                pass
            pass
           