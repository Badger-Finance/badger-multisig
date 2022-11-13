from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console
from brownie import interface

console = Console()

prod = False


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_cow(prod=prod)
    vault.init_curve()

    wbtc = vault.contract(r.treasury_tokens.WBTC)
    weth = vault.contract(r.treasury_tokens.WETH)

    bcrvIbBTC = interface.ISettV4h(r.sett_vaults.bcrvIbBTC, owner=vault.address)
    crvIbBTC = vault.contract(r.treasury_tokens.crvIbBTC)

    vault.take_snapshot(tokens=[bcrvIbBTC.address, wbtc])

    bcrvIbBTC.withdrawAll()

    vault.curve.withdraw_to_one_coin_zapper(
        r.curve.zap_sbtc,
        r.crv_pools.crvSBTC,
        crvIbBTC,
        crvIbBTC.balanceOf(vault),
        wbtc,
    )

    vault.cow.market_sell(wbtc, weth, 40e8, deadline=60 * 60 * 4)

    vault.print_snapshot()
    vault.post_safe_tx()
