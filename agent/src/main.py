import asyncio
import time
import traceback

from config import Config
from helpers import Assert, BalanceHelper,CrossChainATokenBalanceHelper
from optimizer import get_extra_data_for_optimization, optimize_chain_allocation_with_direction
from engine import build_context, StrategyManager, execute_all_rebalance_operations,compute_rebalance_operations, get_allocations, EngineContext
from adapters import Vault
from tee import get_tee_info

async def run_once(context: EngineContext, config: Config):
    print("Remote configs for all chains:", context.remote_configs)

    config.summary()

    is_worker_registered = await context.rebalancer_contract.is_worker_registered(context.near_wallet.account_id)
    print(f"Worker registered: {is_worker_registered}")

    if not is_worker_registered:
        print("Worker not registered. Registering now...")
        
        tee_info = await get_tee_info(context.near_wallet.account_id)

        if tee_info.get("success") is False:
            raise RuntimeError(f"get_tee_info failed: {tee_info.get('error')}")

        quote_hex = tee_info["quote_hex"]
        collateral = tee_info["collateral"]
        checksum = tee_info["checksum"]
        tcb_info = tee_info["tcb_info"]

        print(f"Registering worker with TEE info - Quote Hex: {quote_hex}")
        print(f"Collateral: {collateral}")
        print(f"Checksum: {checksum}")
        print(f"TCB Info: {tcb_info}")
        
        await context.rebalancer_contract.register_worker(
            quote_hex=quote_hex,
            collateral=collateral,
            checksum=checksum,
            tcb_info=tcb_info
        )
        print("Worker registration completed.")

    agent_evm_address = context.agent_address
    vault_address = context.vault_address

    # Get max allowance
    max_allowance = Vault(context.vault_address, context.source_network, context.evm_factory_provider).get_max_total_deposits()
    print(f"Max allowance for vault {vault_address} on source chain: {max_allowance}")
   
   # Configure Crosschain BalanceHelper 
    CrossChainATokenBalanceHelper.configure(
        agent_address=agent_evm_address,
        source_chain_id=context.source_chain_id,
        supported_chains=context.supported_chains,
        remote_configs=context.remote_configs,
        evm_factory_provider=context.evm_factory_provider,
    )

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
      
        usdc_agent_balance_before_in_source_chain = activity_log["usdc_agent_balance_before_in_source_chain"]
        usdc_agent_balance_before_in_dest_chain = activity_log["usdc_agent_balance_before_in_dest_chain"]
        a_usdc_agent_balance_before_in_source_chain = activity_log["a_usdc_agent_balance_before_in_source_chain"]
        a_usdc_agent_balance_before_in_dest_chain = activity_log["a_usdc_agent_balance_before_in_dest_chain"]
        
        # if there is an existing session but the previous step is None, we set the restart_from to pending_step
        if restart_from is None:
            restart_from = existing_session["pending_step"]

        print(f"Resuming from flow: {flow}, from_chain_id: {from_chain_id}, to_chain_id: {to_chain_id}, amount: {amount}, restart_from: {restart_from}")
        
        await StrategyManager.get_strategy(flow).execute(from_chain_id=from_chain_id, 
            to_chain_id=to_chain_id, 
            amount=amount,
            flow=flow,
            restart_from=restart_from, 
            usdc_agent_balance_before_in_source_chain=usdc_agent_balance_before_in_source_chain,
            usdc_agent_balance_before_in_dest_chain=usdc_agent_balance_before_in_dest_chain,
            a_usdc_agent_balance_before_in_source_chain=a_usdc_agent_balance_before_in_source_chain,
            a_usdc_agent_balance_before_in_dest_chain=a_usdc_agent_balance_before_in_dest_chain
        )

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

async def main():
    # Load configuration from environment variables
    config = Config.from_env()

    # Build engine context
    context = await build_context(config)

    interval = config.interval_seconds
    print(f"⏱ Rebalancer interval: {interval}s")

    while True:
        try:
            await run_once(context, config)
        except Exception as e:
            print("❌ run_once failed:", repr(e))
            traceback.print_exc()
            # In case of failure, wait a bit before retrying
            print("Waiting 30s before retrying...")
            await asyncio.sleep(30)

        print(f"🕒 Sleeping {config.interval_seconds:.0f}s until next run")
        await asyncio.sleep(config.interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())
