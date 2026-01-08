from enum import Enum


class Flow(Enum):
    RebalancerToAave = "RebalancerToAave"
    AaveToRebalancer = "AaveToRebalancer"
    AaveToAave       = "AaveToAave"