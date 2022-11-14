from great_ape_safe import GreatApeSafe
from helpers.addresses import registry as r


def main():
    vault = GreatApeSafe(r.eth.badger_wallets.treasury_vault_multisig)
    zap = vault.contract(r.ibbtc.mint_zap)
    wbtc = vault.contract(r.eth.treasury_tokens.WBTC)
    ibbtc = vault.contract(r.eth.treasury_tokens.ibBTC)

    vault.take_snapshot([wbtc, ibbtc])

    mantissa = ibbtc.balanceOf(vault)
    ibbtc.approve(zap, mantissa)
    _, _, min_out, _ = zap.calcRedeemInWbtc(mantissa)
    zap.redeem(wbtc, mantissa, 0, 1, min_out)

    vault.post_safe_tx(skip_preview=True)
