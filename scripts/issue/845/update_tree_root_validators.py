from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    dev = GreatApeSafe(r.badger_wallets.dev_multisig)
    tree = dev.contract(r.badger_wallets.badgertree)

    tree.grantRole(
        tree.ROOT_VALIDATOR_ROLE(), r.badger_wallets["ops_root-validator_v3"]
    )

    # also remove an old one
    tree.revokeRole(
        tree.ROOT_VALIDATOR_ROLE(),
        r.badger_wallets._deprecated["ops_root-validator-old"],
    )

    dev.post_safe_tx(call_trace=True)
