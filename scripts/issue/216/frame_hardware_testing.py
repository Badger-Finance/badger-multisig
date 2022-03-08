from great_ape_safe import GreatApeSafe
from brownie import interface


def main(
    safe_address=None,
    erc20_token=None,
    destination=None,
    action_trigger=0,
    safe_nonce=None,
):
    safe = GreatApeSafe(safe_address)

    erc20_token = interface.IERC20(erc20_token, owner=safe.address)

    erc20_token.transfer(destination, erc20_token.balanceOf(safe))

    safe_nonce = int(safe_nonce) if safe_nonce is not None else None

    if int(action_trigger) == 0:
        safe.post_safe_tx()
    elif int(action_trigger) == 1:
        safe.sign_with_frame_hardware_wallet(safe_nonce)
    else:
        safe.execute_with_frame_hardware_wallet(safe_nonce)
