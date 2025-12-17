from web3 import Web3
from .abis import USDC_ABI

class USDC:
    @staticmethod
    def get_allowance(web3_instance: Web3, usdc_address: str, owner:str, spender: str) -> int:
        """
        Returns the amount of USDC that `spender` is allowed to spend on behalf of `owner`.

        This method calls the ERC20 `allowance(owner, spender)` view function
        on the USDC contract.

        Args:
            web3_instance (Web3): Initialized Web3 instance connected to the target network.
            usdc_address (str): Address of the USDC ERC20 contract.
            owner (str): Address of the token owner.
            spender (str): Address authorized to spend the tokens.

        Returns:
            int: Allowance amount in the smallest USDC unit (6 decimals).
        """
        contract = web3_instance.eth.contract(address=Web3.to_checksum_address(usdc_address), abi=USDC_ABI)

        allowance = contract.functions.allowance(Web3.to_checksum_address(owner), Web3.to_checksum_address(spender)).call()       

        return allowance