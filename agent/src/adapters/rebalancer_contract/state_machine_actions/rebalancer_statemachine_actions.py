from .aave_supply import AaveSupply
from .aave_withdraw import AaveWithdraw
from .cctp_burn import CctpBurn
from .cctp_mint import CctpMint
from .complete_rebalance import CompleteRebalance
from .return_funds import ReturnFunds
from .start_rebalance import StartRebalance
from .withdraw_for_cross_chain_allocation import WithdrawForCrossChainAllocation

class RebalancerStepMachineActions(
    AaveSupply,
    AaveWithdraw,
    CctpBurn,
    CctpMint,
    CompleteRebalance,
    ReturnFunds,
    StartRebalance,
    WithdrawForCrossChainAllocation,
): 
   pass
