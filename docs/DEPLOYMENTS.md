# Deployments

Deployments are stored in the `deployments/` directory.

Each deployment represents a full protocol instance and consists of:

1. Deployment of an `AaveVault` contract in the `source chain`

2. Deployment of a corresponding `Near contract` used by the agent to coordinate and authorize agent actions.

## Deployment files

Each deployment is stored as a JSON file using the following structure:

```json
{
  "index": 1,
  "account_id": "rebalancer-abcdefghi-1.testnet",
  "network": "testnet",
  "path_str": "ethereum-1",
  "evm_address": "0x3c00e24ab8ee6d91c1d4f52afad384f1286ca1df",
  "timestamp": "2025-11-04T17-24-08Z"
}
```

Where:

- index: Sequential identifier for the deployment.
- account_id: NEAR account ID where the rebalancer contract is deployed.
- network: NEAR network used for the deployment (testnet or mainnet).
- path_str: Derivation path used for Chain Signatures and agent authorization (e.g. ethereum-1).
- evm_address: Address of the deployed AaveVault contract on the source EVM chain.
- timestamp: ISO-8601 timestamp indicating when the deployment was executed.

## Deployment script

The full deployment process is automated using the `scripts/deploy.sh` file.

The script ensures that all required components are deployed in the correct order:
	1.	Deploys the AaveVault contract on the selected EVM chain
	2.	Deploys the NEAR rebalancer contract
	3.	Persists the deployment metadata under deployments/

Using the script guarantees consistent and reproducible deployments.

