from enum import Enum


class TxType(Enum):
    AaveSupply                        = "AaveSupply"
    AaveWithdraw                      = "AaveWithdraw"
    CCTPBurn                          = "CCTPBurn"
    CCTPMint                          = "CCTPMint"
    RebalancerWithdrawToAllocate      = "RebalancerWithdrawToAllocate"
    RebalancerUpdateCrossChainBalance = "RebalancerUpdateCrossChainBalance"
    RebalancerDeposit                 = "RebalancerDeposit"
    RebalancerSignCrossChainBalance   = "RebalancerSignCrossChainBalance"
    CompleteRebalance                  = "CompleteRebalance"
    @property
    def as_u8(self) -> int:
        return {
            TxType.AaveSupply: 0,
            TxType.AaveWithdraw: 1,
            TxType.CCTPBurn: 2,
            TxType.CCTPMint: 3,
            TxType.RebalancerWithdrawToAllocate: 4,
            TxType.RebalancerUpdateCrossChainBalance: 5,
            TxType.RebalancerDeposit: 6,
            TxType.RebalancerSignCrossChainBalance: 7,
            TxType.CompleteRebalance: 8,
        }[self]