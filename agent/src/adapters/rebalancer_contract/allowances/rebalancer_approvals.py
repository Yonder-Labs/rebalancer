from .approve_aave import ApproveAave
from .approve_messenger import ApproveMessengerCctp
from .approve_vault import ApproveVault

class RebalancerApprovals(ApproveAave, ApproveMessengerCctp, ApproveVault):
   pass