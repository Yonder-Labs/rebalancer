import asyncio

from config import Config
from helpers import Assert, BalanceHelper
from optimizer import get_extra_data_for_optimization, optimize_chain_allocation_with_direction
from engine import build_context, StrategyManager, execute_all_rebalance_operations,compute_rebalance_operations, get_allocations
from adapters import Vault

async def main():
    # Load configuration from environment variables
    config = Config.from_env()

    # Build engine context
    context = await build_context(config)
    print("Remote configs for all chains:", context.remote_configs)

    agent_evm_address = context.agent_address
    vault_address = context.vault_address

    # Get max allowance
    max_allowance = Vault(context.vault_address, context.source_network, context.evm_factory_provider).get_max_total_deposits()
    print(f"Max allowance for vault {vault_address} on source chain: {max_allowance}")
   
    # Configure Balance Helper
    BalanceHelper.configure(rebalancer_vault_address=vault_address, agent_address=agent_evm_address)

    # Configure Assert
    Assert.configure(rebalancer_vault_address=vault_address, agent_address=agent_evm_address)

    # Configure Strategies
    StrategyManager.configure(rebalancer_contract=context.rebalancer_contract, evm_factory_provider = context.evm_factory_provider, vault_address=vault_address, config=config, remote_config=context.remote_configs, agent_address=agent_evm_address, max_allowance=max_allowance)

    existing_session = await context.rebalancer_contract.get_active_session_info() #  returns [nonce, flow, previous_step, pending_step]

    print("💡Existing session info:", existing_session)

    if existing_session:
        print("Resumed existing rebalance session.")
        flow = existing_session["flow"]
        restart_from = existing_session["previous_step"]

        activity_log = await context.rebalancer_contract.get_activity_log()
        from_chain_id = activity_log["source_chain"]
        to_chain_id = activity_log["destination_chain"]
        amount = activity_log["amount"]
        usdc_agent_balance_before_rebalance = activity_log["usdc_agent_balance_before"]
        
        # if there is an existing session but the previous step is None, we set the restart_from to pending_step
        if restart_from is None:
            restart_from = existing_session["pending_step"]

        print(f"Resuming from flow: {flow}, from_chain_id: {from_chain_id}, to_chain_id: {to_chain_id}, amount: {amount}, restart_from: {restart_from}")
        
        await StrategyManager.get_strategy(flow).execute(from_chain_id=from_chain_id, to_chain_id=to_chain_id, amount=amount, flow=flow, restart_from=restart_from, usdc_agent_balance_before_rebalance=usdc_agent_balance_before_rebalance)

        print("✅ Rebalance operations computed successfully.")

        return

    current_allocations, total_assets_under_management = await get_allocations(context)
    
    extra_data_for_optimization = await get_extra_data_for_optimization(
        total_assets_under_management=total_assets_under_management,
        mpc_wallet=context.mpc_wallet,
        current_allocations=current_allocations,
        configs=context.remote_configs,
        override_interest_rates=config.override_interest_rates,
    )

    optimized_allocations = optimize_chain_allocation_with_direction(data=extra_data_for_optimization)
    print("Optimized Allocations:", optimized_allocations)
    
    rebalance_operations = compute_rebalance_operations(current_allocations, optimized_allocations["allocations"])
    print("Rebalance Operations:", rebalance_operations)

    if not rebalance_operations:
        print("No rebalance operations needed.")
        return

    # Execute Rebalance Operations 
    await execute_all_rebalance_operations(
        source_chain_id=context.source_chain_id,
        rebalance_operations=rebalance_operations
    )
    print("✅ Rebalance operations computed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
