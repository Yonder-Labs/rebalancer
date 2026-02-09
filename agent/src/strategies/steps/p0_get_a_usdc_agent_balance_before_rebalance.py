from adapters import LendingPool
from helpers import BalanceHelper
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName


class GetAUSDCBalanceBeforeRebalance(Step):
    NAME = StepName.GetAUSDCBalanceBeforeRebalance
    
    async def run(self, ctx: StrategyContext) -> None:
        print("Getting AUSDC agent balance before rebalance...")
        
        ctx.a_token_address_on_destination_chain = LendingPool.get_atoken_address(ctx.web3_destination, ctx.aave_lending_pool_address_on_destination_chain, ctx.usdc_token_address_on_destination_chain)

        if ctx.a_token_address_on_destination_chain is None:
            raise ValueError("a_token_address_on_destination_chain is not set in context.")
        
        ctx.a_token_address_on_source_chain = LendingPool.get_atoken_address(ctx.web3_source, ctx.aave_lending_pool_address_on_source_chain, ctx.usdc_token_address_on_source_chain)

        if ctx.a_token_address_on_source_chain is None:
            raise ValueError("a_token_address_on_source_chain is not set in context.")
   
        if ctx.is_restart:
            print("⚠️ Restart detected; skipping fetching AUSDC balance before rebalance.")

            if ctx.a_usdc_agent_balance_before_in_source_chain is None:
                raise ValueError("AUSDC agent balance before rebalance in source chain must be set in context when restarting.")
            
            if ctx.a_usdc_agent_balance_before_in_dest_chain is None:
                raise ValueError("AUSDC agent balance before rebalance in dest chain must be set in context when restarting.")
            
            return
        
        ctx.a_usdc_agent_balance_before_in_source_chain = BalanceHelper.get_atoken_agent_balance(ctx.web3_source, ctx.a_token_address_on_source_chain)

        if ctx.a_usdc_agent_balance_before_in_source_chain is None:
            raise ValueError("a_usdc_agent_balance_before_in_source_chain is not set in context.")
        
        ctx.a_usdc_agent_balance_before_in_dest_chain = BalanceHelper.get_atoken_agent_balance(ctx.web3_destination, ctx.a_token_address_on_destination_chain)

        if ctx.a_usdc_agent_balance_before_in_dest_chain is None:
            raise ValueError("a_usdc_agent_balance_before_in_dest_chain is not set in context.")
        