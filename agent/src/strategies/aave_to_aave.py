from .strategy import Strategy

class AaveToAave(Strategy):
    NAME = "Aave→Aave"
    STEPS = [
        # This strategy directly moves assets from Aave on one chain to Aave on another chain.
    ]
