from typing import Dict, Optional
from near_omni_client.providers.evm.alchemy_provider import AlchemyFactoryProvider

from adapters import RebalancerContract
from config import Config
from engine_types import Flow

from .strategy_context import StrategyContext
from .steps import retry_async_step

class Strategy:
    NAME = "BaseStrategy"
    STEPS: list[type] = []
    COMMON_STEPS: list[type] = []

    def __init__(self, *, rebalancer_contract: RebalancerContract, evm_factory_provider: AlchemyFactoryProvider, vault_address: str, config: Config, remote_config: Dict[str, dict], agent_address: str, max_allowance: int):
        self.rebalancer_contract = rebalancer_contract
        self.evm_factory_provider = evm_factory_provider
        self.vault_address = vault_address
        self.config = config
        self.remote_config = remote_config
        self.agent_address = agent_address
        self.max_allowance = max_allowance

    async def execute(self, *, from_chain_id: int, to_chain_id: int, amount: int, flow: Flow, restart_from: str | None = None, usdc_agent_balance_before_rebalance: Optional[int] = None):
        ctx = self._make_context(
            from_chain_id=from_chain_id,
            to_chain_id=to_chain_id,
            amount=amount,
            flow=flow,
            restart_from=restart_from,
            usdc_agent_balance_before_rebalance=usdc_agent_balance_before_rebalance
        )
        await self._run_phases(ctx, restart_from)

    def _make_context(self, *, from_chain_id: int, to_chain_id: int, flow: Flow, amount: int, restart_from: Optional[str] = None, usdc_agent_balance_before_rebalance: Optional[int] = None) -> StrategyContext:
        print(f"🟩 Flow {self.NAME} | from={from_chain_id} to={to_chain_id} amount={amount}")
        return StrategyContext(
            from_chain_id=from_chain_id,
            to_chain_id=to_chain_id,
            amount=amount,
            remote_config=self.remote_config,
            config=self.config,
            agent_address=self.agent_address,
            vault_address=self.vault_address,
            evm_factory_provider=self.evm_factory_provider,
            rebalancer_contract=self.rebalancer_contract,
            flow=flow,
            max_allowance=self.max_allowance,
            restart_from=restart_from,
            is_restart=restart_from is not None,
            usdc_agent_balance_before_rebalance=usdc_agent_balance_before_rebalance
        )

    async def _run_phases(self, ctx: StrategyContext, restart_from: Optional[str] = None):
        start_index = 0
        required_steps = []

        # find the step to restart from, if applicable
        if restart_from:
            for i, step_cls in enumerate(self.STEPS):
                if step_cls.CAN_BE_RESTARTED and step_cls.PAYLOAD_TYPE == restart_from:
                    start_index = i
                    required_steps = step_cls.REQUIRED_STEPS or []
                    break

        # common steps
        for step_cls in self.COMMON_STEPS:
            await self._run_step(step_cls(), ctx)

        # required steps of target
        if restart_from and required_steps:
            step_map = {cls.NAME: cls for cls in self.STEPS}
            for step_name in required_steps:
                await self._run_step(step_map[step_name](), ctx)

        # normal flow
        for step_cls in self.STEPS[start_index:]:
            await self._run_step(step_cls(), ctx)

    async def _run_step(self, step, ctx):
        print(f"🌈 Phase: {step.NAME.value}")
        if step.SHOULD_BE_RETRIED:
            await retry_async_step(lambda: step.run(ctx))
        else:
            await step.run(ctx)