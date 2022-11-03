from brownie import interface, chain

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    badger = interface.ERC20(registry.eth.treasury_tokens.BADGER, owner=vault.account)
    tree_dripper = vault.contract(registry.eth.drippers.tree_2022_q3)

    vault.take_snapshot([badger])

    # Badger deficit at 11:07 UTC 8th July = 171765.87576753003. Aprox to 172k.
    TREE_DEFICIT = 172_000e18
    # 19k badger which will be emitted between week 27 - 31
    GRAVIAURA_EMISSIONS = 19_000e18

    RELEASABLE = tree_dripper.vestedAmount(
        badger.address, chain.time()
    ) - tree_dripper.released(badger.address)

    DEFICIT_TO_COVER = TREE_DEFICIT + GRAVIAURA_EMISSIONS - RELEASABLE

    # https://github.com/Badger-Finance/badger-multisig/issues/620#issuecomment-1177909957
    badger.transfer(registry.eth.drippers.tree_2022_q3, DEFICIT_TO_COVER)

    vault.post_safe_tx()
