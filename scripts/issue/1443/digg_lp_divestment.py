from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# slippages
COEF = 0.95
DEADLINE = 60 * 60 * 24

BURN_ADDRESS = "0x000000000000000000000000000000000000dEaD"


def main(unwrap="true"):
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_aura()
    vault.init_balancer()
    vault.init_cow(True)

    badger = vault.contract(r.treasury_tokens.BADGER)
    weth = vault.contract(r.treasury_tokens.WETH)
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    digg = vault.contract(r.treasury_tokens.DIGG)
    aura = vault.contract(r.treasury_tokens.AURA)
    bal = vault.contract(r.treasury_tokens.BAL)
    graviaura = vault.contract(r.sett_vaults.graviAURA)

    vault.take_snapshot(tokens=[badger, wbtc, digg, aura, bal, graviaura])

    aura_bpts = [
        vault.contract(r.balancer.B_20_BTC_80_BADGER),
        vault.contract(r.balancer.bpt_40wbtc_40digg_20graviaura),
    ]

    for bpt in aura_bpts:
        vault.aura.unstake_all_and_withdraw_all(bpt)
        if unwrap == "true":
            # Not claiming rewards as these will be processed separately on TCL strat
            vault.balancer.unstake_all_and_withdraw_all(
                pool=bpt, unstake=False, pool_type="Weighted", claim=False
            )

    # Selling graviAURA for wETH as per TCD 36
    aura_before = aura.balanceOf(vault)
    graviaura.withdrawAll()
    aura_witdrawn = aura.balanceOf(vault) - aura_before
    assert aura_witdrawn > 0
    vault.cow.market_sell(aura, weth, aura_witdrawn, deadline=DEADLINE, coef=COEF)

    # Burning all Digg holdings by transfering to the 0xDead address
    vault_digg_balance = digg.balanceOf(vault)
    burn_digg_baalnce = digg.balanceOf(BURN_ADDRESS)
    digg.transfer(BURN_ADDRESS, vault_digg_balance)
    assert digg.balanceOf(vault) == 0
    assert digg.balanceOf(BURN_ADDRESS) - burn_digg_baalnce == vault_digg_balance

    vault.post_safe_tx()
