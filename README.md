# AAVE Rebalancer Agent

The agent is a multichain yield optimizer that optimizes USDC yields across AAVE deployments in multiple chains by dynamically reallocating liquidity to the highest-yielding instance.

Built with NEAR’s [Shade Agent] stack, this system leverages secure off-chain computation and cross-chain messaging [CCTP] to automate rebalancing without compromising custody or control.

The core vault contract follows the ERC-4626 vault standard, and rebalancing logic runs in a trusted execution environment (TEE) to ensure integrity and privacy. 

## Supported chains:

- Ethereum
- Arbitrum
- Base
- OP

## ✨ Features

🚀 **Non custodial**

User funds can only be withdrawn by the original depositor, and only up to the amount deposited. 

🚓 **Secure cross chain execution**

Combines Phala's TEE compute and NEAR's Chain Signatures for trust-minimized automation.

🦄 **Seamless UX**

Users interact with one vault, while the system manages bridging, allocation, and optimization behind the scenes.

## 🚀 Quick Start

```bash
git clone https://github.com/Yonder-Labs/rebalancer.git
cd rebalancer
cp .env.sample .env
```

Update `.env` (minimum for testnet): `ALCHEMY_API_KEY`, `NEAR_NETWORK`, `MNEMONIC_TESTNET`, `SENDER_TESTNET`.

```bash
just setup-dev
./scripts/2-deploy.sh
just run_agent
```

## ⚙️ Configuration

The repo uses a root `.env` file. See `.env.sample` for the full list of options.

Commonly required values:

- `ALCHEMY_API_KEY` - RPC access for EVM chains
- `NEAR_NETWORK` - `near-testnet` or `near-mainnet`
- `MNEMONIC_TESTNET` / `SENDER_TESTNET` - EVM deployer
- `AGENT_ADDRESS` - auto-populated by `scripts/2-deploy.sh`

## 🔎 How It Works

1) User deposits USDC to an ERC-4626 vault contract on the source chain.
2) The USDC is immediately allocated to the AAVE instance in the source chain.
3) The agent verifies periodically whether it’s worthwhile to rebalance, by proactively identifying rate changes across all supported chains.
4) When a meaningful yield delta is detected, the agent evaluates the rebalance by accounting for bridge costs and execution overhead.
5) If profitable, the agent initiates a cross-chain rebalance using CCTP and AAVE, coordinated through the NEAR contract.
6) The agent calculates the shift in Aave rate post-deposit and executes the rebalance across chains.
7) All critical state is stored in the NEAR smart contract. Worker agents can pick up immediately and start executing rebalancing flows.

## 🏗️ Architecture

The system is composed of three main components:

### EVM Smart Contracts

- ERC-4626 compatible vault for USDC deposits and withdrawals

- Chain-local accounting and AAVE integrations

- No off-chain trust assumptions

### NEAR Smart Contract

- Acts as the system coordinator and source of truth

- Stores rebalancing state and flow progress

- Generates and authorizes EVM transaction payloads using Chain Signatures

### Agent

- Runs off-chain inside a trusted execution environment

- Monitors rates and evaluates rebalance opportunities

- Executes rebalancing flows by interacting with the NEAR contract to generate valid chain signatures

## 🔧 Project Structure

The project is a monorepo with the main components:

- `agent/` - Python agent that interacts with the NEAR contract to perform rebalancing.
- `contract/` - NEAR contract that generates signed payloads for EVM execution.
- `contract-evm/` - Extended ERC-4626 vault contracts and deployment scripts.
- `deployments/`
- `docs/`
- `scripts/`

## 📄 Documentation

- [Development Guide](./docs/DEVELOPMENT.md)
- [Architecture Deep Dive](./docs/ARCHITECTURE.md)
- [Design philosophy](./docs/DESIGN.md)
- [Flows](./docs/FLOWS.md)
- [Deployments](./docs/DEPLOYMENTS.md)

## 🪪 License

This project is licensed under the Apache-2.0 License.

<!-- ## References -->

[Shade Agent]: https://docs.near.org/ai/shade-agents/getting-started/introduction
[CCTP]: https://www.circle.com/cross-chain-transfer-protocol

