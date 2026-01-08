import time
from near_omni_client.adapters.cctp.attestation_service import AttestationService
from ..strategy_context import StrategyContext
from .step import Step
from .step_names import StepName
from .constants import POLL_INTERVAL_SECONDS

class WaitAttestation(Step):
    NAME = StepName.WaitAttestation

    async def run(self, ctx: StrategyContext):
        attestation_service = AttestationService(ctx.from_network_id)

        attestation = attestation_service.retrieve_attestation(
            transaction_hash=ctx.burn_tx_hash
        )

        print("✅ Attestation retrieved successfully!")
        
        ctx.attestation = attestation

        time.sleep(POLL_INTERVAL_SECONDS)