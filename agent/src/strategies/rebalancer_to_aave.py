from .strategy import Strategy
from .steps.p0_start_rebalance import StartRebalance
from .steps.p1_withdraw_from_rebalancer import WithdrawFromRebalancer
from .steps.p1_withdraw_from_rebalancer_after_assertion import WithdrawFromRebalancerAfterAssertion
from .steps.p0_get_usdc_agent_balance_before_rebalance import GetUSDCBalanceBeforeRebalance
from .steps.p2_compute_cctp_fees import ComputeCctpFees
from .steps.p0_approve_before_cctp_burn import ApproveBeforeCctpBurnIfRequired
from .steps.p0_approve_aave_before_supply import ApproveAaveUSDCBeforeSupplyIfRequired

from .steps.p2_cctp_burn import CctpBurn
from .steps.p2_cctp_burn_after_assertion import CctpBurnAfterAssertion
from .steps.p3_wait_attestation import WaitAttestation
from .steps.p4_cctp_mint import CctpMint
from .steps.p4_cctp_mint_after_assertion import CctpMintAfterAssertion
from .steps.p5_get_a_token_agent_balance_before_supply import GetATokenBalanceBeforeSupply
from .steps.p5_supply_aave import SupplyAave
from .steps.p5_supply_aave_after_assertion import SupplyAaveAfterAssertion
from .steps.p6_complete_rebalance import CompleteRebalance

class RebalancerToAave(Strategy):
    NAME = "Rebalancer→Aave"
    COMMON_STEPS=[
        ApproveBeforeCctpBurnIfRequired, # @dev we execute the allowances check before all
        ApproveAaveUSDCBeforeSupplyIfRequired, # @dev we execute the allowances check before all
        GetUSDCBalanceBeforeRebalance,
    ]
    STEPS = [
        StartRebalance,
        WithdrawFromRebalancer,
        WithdrawFromRebalancerAfterAssertion,
        ComputeCctpFees,
        CctpBurn,
        CctpBurnAfterAssertion,
        WaitAttestation,
        CctpMint,
        CctpMintAfterAssertion,
        GetATokenBalanceBeforeSupply,
        SupplyAave,
        SupplyAaveAfterAssertion,
        CompleteRebalance,
    ]