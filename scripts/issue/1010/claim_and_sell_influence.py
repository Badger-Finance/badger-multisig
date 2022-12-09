from great_ape_safe import GreatApeSafe
from helpers.addresses import r


prod = False


def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    safe.init_badger()
    safe.init_cow(prod=prod)

    bvecvx = safe.contract(r.treasury_tokens.bveCVX)
    bcvxcrv = safe.contract(r.treasury_tokens.bcvxCRV)
    gravi = safe.contract(r.sett_vaults.graviAURA)
    baurabal = safe.contract(r.sett_vaults.bauraBal)

    alcx = safe.contract(r.treasury_tokens.ALCX)
    spell = safe.contract(r.treasury_tokens.SPELL)
    ldo = safe.contract(r.bribe_tokens_claimable_graviaura.LDO)
    angle = safe.contract(r.treasury_tokens.ANGLE)
    bal = safe.contract(r.treasury_tokens.BAL)
    fxs = safe.contract(r.treasury_tokens.FXS)

    dai = safe.contract(r.treasury_tokens.DAI)
    weth = safe.contract(r.treasury_tokens.WETH)

    sell_to_dai = [bvecvx, bcvxcrv, gravi, baurabal]
    sell_to_weth = [alcx, spell, ldo, angle, bal, fxs]

    safe.take_snapshot(tokens=sell_to_dai)

    safe.badger.claim_all()

    for token in sell_to_dai:
        safe.cow.market_sell(token, dai, token.balanceOf(safe), 60 * 60 * 4)

    for token in sell_to_weth:
        safe.cow.market_sell(token, weth, token.balanceOf(safe), 60 * 60 * 4)

    safe.post_safe_tx()
