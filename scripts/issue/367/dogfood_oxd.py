from brownie import interface

from helpers.addresses import registry
from great_ape_safe import GreatApeSafe


def main():
    '''
    dogfood half oxd into bveoxd,
    lp into bveoxd/oxd,
    dogfood lp into bbveoxd/oxd
    '''
    trops = GreatApeSafe(registry.ftm.badger_wallets.treasury_ops_multisig)

    oxd = interface.ERC20(registry.ftm.treasury_tokens.OXD, owner=trops.account)
    bveoxd = interface.ISettV4h(registry.ftm.sett_vaults.bveOXD, owner=trops.account)
    bveoxd_oxd = interface.IUniswapV2Pair(registry.ftm.lp_tokens['bveOXD-OXD'], owner=trops.account)
    bbveoxd_oxd = interface.ISettV4h(registry.ftm.sett_vaults['bbveOXD-OXD'], owner=trops.account)

    trops.init_solidly()
    trops.take_snapshot(tokens=[oxd, bbveoxd_oxd])

    half_oxd = oxd.balanceOf(trops) / 2
    oxd.approve(bveoxd, half_oxd)
    bveoxd.deposit(half_oxd)

    oxd_bal = oxd.balanceOf(trops)
    trops.solidly.add_liquidity(oxd, bveoxd, mantissaA=oxd_bal)

    lp_bal = bveoxd_oxd.balanceOf(trops) * 0.99 # dusty
    bveoxd_oxd.approve(bbveoxd_oxd, lp_bal)
    bbveoxd_oxd.deposit(lp_bal)

    trops.print_snapshot()

    trops.post_safe_tx()
