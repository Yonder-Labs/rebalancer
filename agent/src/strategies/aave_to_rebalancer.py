from .strategy import Strategy

from .steps.p0_start_rebalance import StartRebalance
from .steps.p0_get_usdc_agent_balance_before_rebalance import GetUSDCBalanceBeforeRebalance
from .steps.p0_approve_before_cctp_burn import ApproveBeforeCctpBurnIfRequired
from .steps.p0_approve_vault_to_spend_agent_usdc import ApproveVaultToSpendAgentUSDCIfRequired

from .steps.p2_compute_cctp_fees import ComputeCctpFees
from .steps.p2_cctp_burn import CctpBurn
from .steps.p2_cctp_burn_after_assertion import CctpBurnAfterAssertion
from .steps.p3_wait_attestation import WaitAttestation
from .steps.p4_cctp_mint import CctpMint
from .steps.p4_cctp_mint_after_assertion import CctpMintAfterAssertion
from .steps.p6_complete_rebalance import CompleteRebalance
from .steps.p6_withdraw_from_aave import WithdrawFromAave
from .steps.p6_withdraw_from_aave_after_assertion import WithdrawFromAaveAfterAssertion
from .steps.p7_deposit_into_rebalancer import DepositIntoRebalancer
from .steps.p7_deposit_into_rebalancer_after_assertion import DepositIntoRebalancerAfterAssertion
from .steps.p9_get_usdc_balance_before_deposit_to_rebalancer import GetUSDCBalanceBeforeDepositToRebalancer 

class AaveToRebalancer(Strategy):
    NAME = "Aave→Rebalancer"
    COMMON_STEPS=[
        ApproveBeforeCctpBurnIfRequired, # @dev we execute the allowances check before all
        ApproveVaultToSpendAgentUSDCIfRequired, # @dev we execute the allowances check before all
        GetUSDCBalanceBeforeRebalance,
    ]
    STEPS = [
        StartRebalance,
        WithdrawFromAave,
        WithdrawFromAaveAfterAssertion,
        ComputeCctpFees,
        CctpBurn,
        CctpBurnAfterAssertion,
        WaitAttestation,
        CctpMint,
        CctpMintAfterAssertion,
        GetUSDCBalanceBeforeDepositToRebalancer,
        DepositIntoRebalancer,
        DepositIntoRebalancerAfterAssertion,
        CompleteRebalance
    ]

