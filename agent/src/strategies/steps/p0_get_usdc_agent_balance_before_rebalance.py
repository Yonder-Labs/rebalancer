from helpers import BalanceHelper
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName


class GetUSDCBalanceBeforeRebalance(Step):
    NAME = StepName.GetUSDCBalanceBeforeRebalance
    
    async def run(self, ctx: StrategyContext) -> None:
        print("Getting USDC agent balance before rebalance...")
        
        if ctx.is_restart:
            print("⚠️ Restart detected; skipping fetching USDC balance before rebalance.")

            if ctx.usdc_agent_balance_before_in_source_chain is None:
                raise ValueError("USDC agent balance before rebalance in source chain must be set in context when restarting.")
            
            if ctx.usdc_agent_balance_before_in_dest_chain is None:
                raise ValueError("USDC agent balance before rebalance in dest chain must be set in context when restarting.")
            
            return
        
        ctx.usdc_agent_balance_before_in_source_chain = BalanceHelper.get_usdc_agent_balance(ctx.web3_source, ctx.usdc_token_address_on_source_chain)
        
        if ctx.usdc_agent_balance_before_in_source_chain is None:
            raise ValueError("USDC agent balance before rebalance in source chain is not set in context.")
        
        ctx.usdc_agent_balance_before_in_dest_chain = BalanceHelper.get_usdc_agent_balance(ctx.web3_destination, ctx.usdc_token_address_on_destination_chain)
        
        if ctx.usdc_agent_balance_before_in_dest_chain is None:
            raise ValueError("USDC agent balance before rebalance in dest chain is not set in context.")
        