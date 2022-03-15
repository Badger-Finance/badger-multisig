from brownie import Contract
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


AMOUNT = 1 # WORK to unstake


def main():
    safe = GreatApeSafe(registry.poly.badger_wallets.ops_multisig)
    safe.init_opolis()

    work = Contract(registry.poly.coingecko_tokens.WORK)

    safe.take_snapshot(tokens=[
        work.address
    ])
    
    safe.opolis.unstake(AMOUNT * 10 ** work.decimals())

    safe.print_snapshot()

    safe.post_safe_tx()
