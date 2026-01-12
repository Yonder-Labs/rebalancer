from dstack_sdk import TappdClient
from nacl.encoding import RawEncoder
from nacl.signing import SigningKey
import base58
import secrets
import hashlib

class KeyPairGenerator:
    def __init__(self):
        """
        Initialize KeyPairGenerator instance
        """
        self.account_id = None
        self.signing_key = None
        self.client = TappdClient()
            
    def derive_ephemeral_account(self):
        """Generate ephemeral account using TEE entropy"""
        if self.account_id and self.signing_key:
            raise ValueError("An account is already configured. Cannot generate ephemeral account")
        
        print(f"🔐 Generating ephemeral account with TEE")
        
        random_array = secrets.token_bytes(32) 
        random_string = random_array.hex()
        key_from_tee = self.client.derive_key(random_string, random_string)
        
        tee_bytes = key_from_tee.toBytes(32)
        combined = random_array + tee_bytes
        
        hash_bytes = hashlib.sha256(combined).digest()
        self.signing_key = SigningKey(seed=hash_bytes, encoder=RawEncoder)
        public_key_b58 = base58.b58encode(self.signing_key.verify_key.encode()).decode(
                "utf-8"
        )
        verify_key = self.signing_key.verify_key
        secret_key_bytes = self.signing_key.encode() + verify_key.encode()
        secret_key = base58.b58encode(secret_key_bytes).decode('utf-8')
        
        self.account_id = self.get_implicit_account_id()
        print(f"✅ Ephemeral account created: {self.account_id}, public key: {public_key_b58}")
        return self.account_id, f"ed25519:{secret_key}"

    def get_implicit_account_id(self):
        """Convert public key to implicit account ID"""
        if not self.signing_key:
            raise ValueError("Signing key not initialized")
        
        # Get the verify key (public key) from the signing key
        verify_key = self.signing_key.verify_key
        public_key_bytes = verify_key.encode()
        implicit_account = public_key_bytes.hex().lower()
        
        if len(implicit_account) != 64:
            raise ValueError(f"Invalid public key length. Expected 64 chars, got {len(implicit_account)}")
        
        return implicit_account

   