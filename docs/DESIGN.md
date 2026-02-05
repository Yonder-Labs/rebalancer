# Design Philosophy

This document explains the core design choices behind the rebalancer agent, with references to the actual implementation in this repository.

## Goals

- **Non-custodial by design**: user funds stay in the ERC-4626 vault and can only be withdrawn by the depositor.
- **Cross-chain yield optimization**: allocate USDC across Aave deployments on multiple chains based on interest rates.
- **Trust-minimized automation**: use a TEE-backed worker and NEAR Chain Signatures to coordinate EVM actions.
- **Recoverable execution**: flows can be resumed safely after interruptions.
- **Automatic retry and payload reuse**: avoid re-signing and safely retry by reusing cached payloads when available.

## Key design principles

### Single source of truth on NEAR

The NEAR contract stores the system state (active sessions, logs, configs) and enforces the step order for any cross-chain flow. This prevents out-of-order execution and makes progress traceable and resumable.

### Deterministic, step-based flows

Rebalancing is modeled as a fixed sequence of steps with explicit pre/post checks. Each strategy in `agent/src/strategies` is a list of steps in `agent/src/strategies/steps`, which makes flows explicit and auditable.

### Idempotent execution

Each step can re-use a previously signed payload when resuming. The agent checks for existing signatures and only rebuilds and signs payloads when required, reducing the risk of double-execution.

### Payload propagation and caching

Signed payloads are cached on the NEAR contract by `(nonce, step)` and fetched by the agent when restarting. This lets payloads propagate across retries without re-signing and provides a consistent source of truth for what should be broadcast on each chain.

### Separation of decision and execution

The optimizer computes *what* should move (allocations and operations), while the strategies and steps define *how* to execute those moves across chains. This keeps the decision logic independent from the execution pipeline.

### Configuration as contract state

All chain-specific addresses (Aave pools, CCTP endpoints, vault address, etc.) are fetched from the NEAR contract config and cached in the agent context, so the agent remains stateless and deterministic across restarts.

## Operational lifecycle

1. The agent initializes a context (NEAR client, EVM providers, MPC wallet, remote configs).
2. It computes current allocations using on-chain balances.
3. It calculates optimal allocations and derives rebalance operations.
4. It executes the matching strategy flow and persists progress via the NEAR contract.
5. If interrupted, it resumes from the last recorded step.

## Trust boundaries

- **Agent**: runs in a TEE and requests signatures from NEAR; it does not custody user funds.
- **NEAR contract**: signs EVM payloads, stores state, and enforces step order.
- **EVM contracts**: hold funds and integrate with Aave and CCTP.

For more details on execution flows, see `docs/FLOWS.md`. For architecture details, see `docs/ARCHITECTURE.md`.
