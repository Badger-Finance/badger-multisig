from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Wei

# https://opensea.io/assets/0xe1e546e25a5ed890dff8b8d005537c0d373497f8/1
token_id = 1

# one time-off addr, not adding in book
recipient = "0xdE0AEf70a7ae324045B7722C903aaaec2ac175F5"


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.ops_multisig_old)
    # only for eth matters here
    safe.take_snapshot(tokens=[])

    # eth transfer to techops
    safe.account.transfer(registry.eth.badger_wallets.techops_multisig, Wei("2 ether"))

    # nft jersey transfer to vault msig
    jersey_nft = safe.contract(registry.eth.nft.badger_jersey)

    # apparently we got 11 units
    jersey_amount = jersey_nft.balanceOf(safe, token_id)

    recipient_amount = jersey_nft.balanceOf(recipient, token_id)

    # 1 unit send to recipient
    jersey_nft.safeTransferFrom(
        safe,
        recipient,
        token_id,
        1,
        bytes(),
    )

    jersey_nft.safeTransferFrom(
        safe,
        registry.eth.badger_wallets.treasury_vault_multisig,
        token_id,
        jersey_amount - 1,
        bytes(),
    )

    assert jersey_nft.balanceOf(recipient, token_id) == recipient_amount + 1

    assert (
        jersey_nft.balanceOf(
            registry.eth.badger_wallets.treasury_vault_multisig, token_id
        )
        == jersey_amount - 1
    )

    safe.print_snapshot()

    # nonces are messed up
    safe.post_safe_tx(replace_nonce=78)
