import base64
import asyncio

from near_omni_client.json_rpc.client import NearClient
from near_omni_client.wallets.near_wallet import NearWallet
from near_omni_client.transactions import TransactionBuilder, ActionFactory
from near_omni_client.transactions.utils import decode_key
from near_omni_client.json_rpc.exceptions import JsonRpcError

FUNDING_DELAY = 60 # seconds

class FundManager:
    def __init__(self, near_wallet: NearWallet, near_client: NearClient):
        self.near_wallet = near_wallet
        self.near_client = near_client

    async def fund_one_time_signer(
        self,
        required_balance_in_near: float,
        destination_account_id: str,
    ):
        print("Checking if one-time signer needs funding...")
        current_balance = await self.near_client.view_account(
            account_id=self.near_wallet.account_id,
        )

        print(f"Current balance for master funder with account id: {self.near_wallet.account_id}: {current_balance.amount} yoctoNEAR")
        # validate the master funder has enough balance
        if int(current_balance.amount) < int(required_balance_in_near * 10**24):
            raise ValueError(
                f"Master funder account {self.near_wallet.account_id} has insufficient balance to fund one-time signer."
            )

        # drip funds to one time signer
        print(f"Funding one-time signer {destination_account_id} with {required_balance_in_near} NEAR...")
        await self._sign_and_submit_transaction(
            receiver_id=destination_account_id,
            amount=int(required_balance_in_near * 10**24),
            max_retries=10
        )
    
    async def _sign_and_submit_transaction(self, *, receiver_id: str, amount: int, max_retries: int = 3, delay: float = 2.0):
      public_key_str = await self.near_wallet.get_public_key()
      signer_account_id = self.near_wallet.get_address()
      private_key_str = self.near_wallet.keypair.to_string()
      nonce_and_block_hash = await self.near_client.get_nonce_and_block_hash(signer_account_id, public_key_str)
      
      tx = (
            TransactionBuilder()
            .with_signer_id(signer_account_id)
            .with_public_key(public_key_str)
            .with_nonce(nonce_and_block_hash["nonce"])
            .with_receiver(receiver_id)
            .with_block_hash(nonce_and_block_hash["block_hash"])
            .add_action(
               ActionFactory.transfer(deposit=amount)
            )
            .build()
      )

      private_key_bytes = decode_key(private_key_str)
      signed_tx = tx.to_vec(private_key_bytes)
      signed_tx_bytes = bytes(bytearray(signed_tx))
      signed_tx_base64 = base64.b64encode(signed_tx_bytes).decode("utf-8")
      
      # --- Retry section starts here ---
      for attempt in range(1, max_retries + 1):
            try:
               print(f"Sending transaction to NEAR network... (attempt {attempt})")
               result = await self.near_client.send_raw_transaction(signed_tx_base64)
               print("✅ Transaction successfully sent.")
               return result
            except JsonRpcError as e:
                msg = str(e)
                if "TIMEOUT_ERROR" in msg:
                  if attempt < max_retries:
                        print(f"⚠️  Timeout error on attempt {attempt}. Retrying in {delay:.1f}s...")
                        await asyncio.sleep(delay)
                        delay *= 2  # exponential backoff
                        continue
                  else:
                        print("❌ Transaction failed after maximum retries due to TIMEOUT_ERROR.")

                if "LackBalanceForState" in msg:
                    print("⚠️  Not enough balance for storage/state.")
                    print("👉 Please fund the signer account and press Ctrl+C to abort.")
                    print(f"⏳ Waiting {FUNDING_DELAY:.0f}s before retrying...")

                    await asyncio.sleep(FUNDING_DELAY)
                    delay *= 2  # exponential backoff
                    continue
                
                raise
            except Exception as e:
               # Catch unexpected errors (network, aiohttp, etc.)
                if attempt < max_retries:
                  print(f"⚠️  Unexpected error on attempt {attempt}: {e}. Retrying in {delay:.1f}s...")
                  await asyncio.sleep(delay)
                  delay *= 2
                  continue
                else:
                    print("❌ Transaction failed after maximum retries due to unexpected error.")
                    raise
      # --- Retry section ends here ---
      
