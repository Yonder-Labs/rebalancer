# Flows

As previously mentioned, the Aave Rebalancer requires a source chain EVM contract as the central place where deposits and withdrawals happen, it means the funds can be moved in different ways but limited to 3 main strategies:

- Rebalancer (source chain) -> Aave instance (destination chain)
- Aave instance (destionatoon chain) -> Rebalancer (source chain)
- Aave instance (destination chain) -> Aave instance (destination chain)

These strategies are defined in `agent/src/strategies`. 

## What's a strategy?

A strategy is a sequence of steps that are designed to fullfil a goal: Move funds from one chain to another.

Steps are independent actions (`agent/src/strategies/steps`) that are independent but sometimes require other steps to run in order to work properly. 

Some examples of steps are:

- Balance checks
- Allowance approvals
- CCTP bridging (burn/mint)
- Aave deposits and withdrawals
- Rebalancer deposits / Withdrawals 

## Rebalancer -> Aave instance

Defined in `agent/src/strategies/rebalancer_to_aave.py` as `Rebalancer→Aave`.

Money flow:

1. Checks and approvals:
   - `ApproveBeforeCctpBurnIfRequired` ensures USDC approval for CCTP burn on the source chain.
   - `ApproveAaveUSDCBeforeSupplyIfRequired` ensures approval for Aave supply on the destination chain.
   - `GetUSDCBalanceBeforeRebalance` and `GetAUSDCBalanceBeforeRebalance` capture pre-rebalance balances.
2. Start rebalance: `StartRebalance` registers the flow in the rebalancer contract.
3. Exit rebalancer on source chain: `WithdrawFromRebalancer`.
4. CCTP bridge:
   - `ComputeCctpFees` calculates bridge fees.
   - `CctpBurn` burns USDC on the source chain.
   - `WaitAttestation` retrieves the attestation.
   - `CctpMint` mints USDC on the destination chain.
5. Enter Aave on destination chain: `SupplyAave`.
6. Finalize: `CompleteRebalance`.

The `*AfterAssertion` variants run as post-action validations after each critical step.

## Aave -> Rebalancer (cross-chain)

Defined in `agent/src/strategies/aave_to_rebalancer.py` as `Aave→Rebalancer`.

Money flow:

1. Checks and approvals:
   - `ApproveBeforeCctpBurnIfRequired` ensures USDC approval for CCTP burn on the source chain.
   - `ApproveVaultToSpendAgentUSDCIfRequired` ensures approval for the vault to receive funds on the destination chain.
   - `GetUSDCBalanceBeforeRebalance` and `GetAUSDCBalanceBeforeRebalance` capture pre-rebalance balances.
2. Start rebalance: `StartRebalance`.
3. Withdraw from Aave on source chain: `WithdrawFromAave`.
4. CCTP bridge:
   - `ComputeCctpFees`.
   - `CctpBurn` on the source chain.
   - `WaitAttestation`.
   - `CctpMint` on the destination chain.
5. Deposit into destination rebalancer (vault): `DepositIntoRebalancer`.
6. Finalize: `CompleteRebalance`.

The `*AfterAssertion` variants run as post-action validations after each critical step.

## Aave -> Aave (cross-chain)

Defined in `agent/src/strategies/aave_to_aave.py` as `Aave→Aave`.

This file currently contains a placeholder only and has no implemented steps. When implemented, it should follow a sequence similar to:

- Withdraw from Aave on the source chain.
- CCTP bridge (burn/mint).
- Supply to Aave on the destination chain.

If you want this flow to be operational, I can implement the strategy and document the exact steps.