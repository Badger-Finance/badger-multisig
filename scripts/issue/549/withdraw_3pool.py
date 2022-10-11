from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    trops.init_curve()

    crv3pool = trops.contract(registry.eth.treasury_tokens.crv3pool)
    usdc = trops.contract(registry.eth.treasury_tokens.USDC)

    trops.take_snapshot(tokens=[crv3pool.address, usdc.address])
    vault.take_snapshot(tokens=[usdc.address])

    trops.curve.withdraw_to_one_coin(crv3pool, crv3pool.balanceOf(trops), usdc)
    usdc.transfer(vault, usdc.balanceOf(trops))

    trops.print_snapshot()
    vault.print_snapshot()

    trops.post_safe_tx()
