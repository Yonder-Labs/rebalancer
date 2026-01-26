#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/approve-codehash.sh <CODEHASH>

CODEHASH="${1:?Missing CODEHASH argument}"

# Load environment variables (expects NEAR_CONTRACT_ACCOUNT and optionally NEAR_NETWORK)
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi

CONTRACT_ID="${NEAR_CONTRACT_ACCOUNT:?NEAR_CONTRACT_ACCOUNT not set in .env}"

# Normalize NEAR network for near-cli
case "${NEAR_NETWORK:-testnet}" in
  near-testnet|testnet)
    NETWORK_ID="testnet"
    ;;
  near-mainnet|mainnet)
    NETWORK_ID="mainnet"
    ;;
  *)
    echo "❌ Unsupported NEAR_NETWORK value: ${NEAR_NETWORK}"
    echo "   Expected: near-testnet | testnet | near-mainnet | mainnet"
    exit 1
    ;;
esac

# Basic sanity check (64 hex chars, lowercase)
if ! [[ "$CODEHASH" =~ ^[0-9a-f]{64}$ ]]; then
  echo "❌ Invalid codehash format"
  echo "   Expected 64 lowercase hex characters"
  exit 1
fi

echo "✅ Approving codehash"
echo "   contract: $CONTRACT_ID"
echo "   network:  $NETWORK_ID"
echo "   codehash: $CODEHASH"

near call \
  --use-account "$CONTRACT_ID" \
  "$CONTRACT_ID" \
  --network-id "$NETWORK_ID" \
  approve_codehash \
  "{\"codehash\":\"$CODEHASH\"}" \
  --deposit 0

echo "🎉 Codehash approved successfully"