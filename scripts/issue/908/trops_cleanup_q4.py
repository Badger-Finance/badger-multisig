from great_ape_safe import GreatApeSafe
from helpers.addresses import r


DEADLINE = 60 * 60 * 4
TREE_DEFICIT = 7200e18


def main():
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    tree = GreatApeSafe(r.badger_wallets.badgertree)
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

    trops.init_badger()
    trops.init_cow(prod=False)

    weth = trops.contract(r.treasury_tokens.WETH)

    eurs = trops.contract(r.treasury_tokens.EURS)
    usdc = trops.contract(r.treasury_tokens.USDC)
    fei = trops.contract(r.treasury_tokens.FEI)
    frax = trops.contract(r.treasury_tokens.FRAX)

    bvecvx = trops.contract(r.treasury_tokens.bveCVX)
    bcvxcrv = trops.contract(r.treasury_tokens.bcvxCRV)
    gravi = trops.contract(r.sett_vaults.graviAURA)
    ibbtc = trops.contract(r.treasury_tokens.ibBTC)

    trops.take_snapshot(tokens=[bvecvx, bcvxcrv, gravi, crvIbBTC.address])
    tree.take_snapshot(tokens=[bcvxcrv])
    vault.take_snapshot(tokens=[crvIbBTC.address, weth])

    trops.badger.claim_all()

    bcvxcrv.transfer(tree, TREE_DEFICIT)
    crvIbBTC.transfer(vault, crvIbBTC.balanceOf(trops))
    weth.transfer(vault, weth.balanceOf(trops))

    trops.cow.market_sell(eurs, usdc, eurs.balanceOf(trops), DEADLINE)
    trops.cow.market_sell(fei, usdc, fei.balanceOf(trops), DEADLINE)
    trops.cow.market_sell(frax, usdc, frax.balanceOf(trops), DEADLINE)

    trops.print_snapshot()
    tree.print_snapshot()
    vault.print_snapshot()

    trops.post_safe_tx()
