# Development

## Prerequisites

- [just] - Task runner used across the repo
- [rust] - Build the NEAR contract
- [cargo-near] - NEAR contract build tooling
- [near-cli] - Deploy and call the NEAR contract
- [python] (3.11+) - Agent runtime
- [uv] - Python dependency manager
- [foundry] - Compile/deploy EVM contracts
- [docker] - Reproducible NEAR builds (`just build-with-docker`)
- [node.js] - Required for `scripts/gen-init-args.js`
- [jq] - Used by `scripts/2-deploy.sh`

## Environment Setup

1) Copy the sample environment file:

```bash
cp .env.sample .env
```

2) Fill in the required values (minimum for testnet):

```bash
# global
ALCHEMY_API_KEY="<Your Alchemy API Key Here>"

# agent
NEAR_NETWORK="near-testnet"

# contract-evm
MNEMONIC_TESTNET="<Your Testnet Mnemonic Here>"
SENDER_TESTNET="<Your Testnet Sender Address Here>"
```

Environment variable reference (from `.env.sample`):

- global
  - `ALCHEMY_API_KEY` - RPC access for EVM chains
- agent
  - `NEAR_NETWORK` - `near-testnet` or `near-mainnet`
  - `NEAR_CONTRACT_ACCOUNT` - Set by `scripts/2-deploy.sh`
  - `MAX_BRIDGE_FEE`, `MIN_BRIDGE_FINALITY_THRESHOLD`, `CALLBACK_GAS_TGAS`
  - `OVERRIDE_INTEREST_RATES` - Optional map for local overrides
  - `KDF_PATH` - Key derivation path used by the agent
  - `USE_STATIC_SIGNER` / `MASTER_FUNDER_*` - Signer configuration
  - `DSTACK_SIMULATOR_ENDPOINT`, `TAPPD_SIMULATOR_ENDPOINT` - TEE simulator sockets
  - `RUN_INTERVAL_SECONDS` - Agent loop interval
- contract-evm
  - `MNEMONIC_*`, `SENDER_*` - Deployers per network
  - `ETHERSCAN_API_KEY` - Optional verification tooling
  - `AGENT_ADDRESS` - Auto-updated by `scripts/2-deploy.sh`

## Getting Started

```bash
$ git clone https://github.com/Yonder-Labs/rebalancer.git
$ cd rebalancer
$ just setup-dev
```

To deploy and run the agent (testnet defaults), use:

```bash
$ ./scripts/2-deploy.sh

$ just run_agent
```

Deployment flow (`scripts/2-deploy.sh`):

1) Create a new NEAR account.
2) Derive the agent EVM address.
3) Save deployment metadata in `deployments/`.
4) Update `.env` with `AGENT_ADDRESS` and `NEAR_CONTRACT_ACCOUNT`.
5) Deploy EVM contracts and seed the agent.
6) Deploy the NEAR contract with init args.

## Compilation

Ensure the project compiles by running:

```bash
$ just build-contract # for a quick check

$ just build-with-docker # for testnet and production mode
```

## Commands

```bash
just create-account <account-name>
```

Example:

```bash
just create-account first-account.testnet
```

## Scripts

Useful automation scripts:

- `scripts/1-setup.sh` - Install deps and build all components.
- `scripts/0-common.sh` - Shared helpers (e.g., `update_env_var`).
- `scripts/2-deploy.sh` - Create a NEAR account, derive agent address, deploy EVM + NEAR contracts, update `.env`.
- `scripts/3-run-all.sh` - Run the agent and an override run.
- `scripts/4-register-codehash.sh` - Approve a new NEAR contract codehash.
- `scripts/gen-init-args.js` - Build init args from `config.json` and EVM deployments.

<!-- ## References -->
[just]: https://github.com/casey/just
[rust]: https://rust-lang.org/learn/get-started/
[cargo-near]: https://github.com/near/cargo-near
[near-cli]: https://docs.near.org/tools/near-cli
[python]: https://www.python.org/downloads/
[uv]: https://github.com/astral-sh/uv
[foundry]: https://book.getfoundry.sh/
[docker]: https://docs.docker.com/
[node.js]: https://nodejs.org/
[jq]: https://jqlang.github.io/jq/