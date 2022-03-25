from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def post_empty_tx():
    safe = GreatApeSafe(registry.eth.badger_wallets.test_multisig_v1_3)
    safe.account.transfer(safe, 0)
    safe.post_safe_tx()


def sign_with_frame(safe_nonce=None):
    safe = GreatApeSafe(registry.eth.badger_wallets.test_multisig_v1_3)
    safe.sign_with_frame_hardware_wallet(safe_nonce)


def exec_with_frame(safe_nonce=None):
    safe = GreatApeSafe(registry.eth.badger_wallets.test_multisig_v1_3)
    safe.execute_with_frame_hardware_wallet(safe_nonce)
