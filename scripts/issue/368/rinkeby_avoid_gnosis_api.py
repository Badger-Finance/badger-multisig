from brownie import accounts, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.rinkeby.badger_wallets.rinkeby_multisig)
    dai = interface.ERC20(
        registry.rinkeby.treasury_tokens.DAI, owner=safe.account
    )
    dai.transfer(safe, 1_000_000e18)
    dai.transfer(safe, 2_000_000e18)

    safe_tx = safe.post_safe_tx(events=False, silent=True, post=False)
    safe_tx.signatures = b''
    print(safe_tx.signatures)
    print(safe_tx.signatures.hex())
    safe.sign_with_frame(safe_tx)
    print(safe_tx.signatures)
    print(safe_tx.signatures.hex())

    print('destination:\t', safe.account)
    print('hex data:\t', interface.IGnosisSafe_v1_3_0(safe).execTransaction.encode_input(
        safe_tx.to, # address to
        safe_tx.value, # uint256 value
        safe_tx.data.hex(), # bytes memory data
        safe_tx.operation, # uint8 operation
        safe_tx.safe_tx_gas, # uint256 safeTxGas
        safe_tx.base_gas, # uint256 baseGas
        safe_tx.gas_price, # uint256 gasPrice
        safe_tx.gas_token, # address gasToken
        safe_tx.refund_receiver, # address refundReceiver
        safe_tx.signatures.hex() # bytes memory signatures
    ))
