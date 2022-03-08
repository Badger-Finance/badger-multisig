from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    """
    claim dropt-3 from tree and redeem for bdigg -> digg
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    safe.init_badger()

    digg = registry.eth.treasury_tokens.DIGG
    bdigg = interface.ISettV4h(registry.eth.treasury_tokens.bDIGG, owner=safe.address)
    dropt = safe.contract(registry.eth.uma.DIGG_LongShortPair)
    dropt_long = safe.contract(dropt.longToken())


    safe.take_snapshot(tokens=[
        bdigg.address,
        digg,
        dropt_long
    ])

    safe.badger.claim_all()

    dropt_long_bal = dropt_long.balanceOf(safe)
    # redeem dropt-3 for bdigg
    dropt.settle(dropt_long_bal, 0)
    
    bdigg.withdrawAll()

    safe.print_snapshot()
    safe.post_safe_tx()
