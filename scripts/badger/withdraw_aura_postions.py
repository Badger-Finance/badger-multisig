from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import Contract

console = Console()

BADGER80WBTC20 = r.balancer.B_20_BTC_80_BADGER
BADGER50RETH50 = r.balancer.B_50_BADGER_50_RETH
WBTC40DIGG40GRAVI20 = r.balancer.bpt_40wbtc_40digg_20graviaura

BADGER80WBTC20_AURA = r.aura.aura_20wbtc80badger
BADGER50RETH50_AURA = r.aura.aura_50reth50badger
WBTC40DIGG40GRAVI20_AURA = r.aura.aura_40wbtc40digg20gravi

AURA_VAULTS = [
    "b80BADGER_20WBTC",
    "b40WBTC_40DIGG_20graviAURA",
    "bBB_a_USD",
    "b33auraBAL_33graviAURA_33WETH",
    "bB_stETH_STABLE",
    "bB_rETH_STABLE"
]

def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_aura()

    bal = vault.contract(r.treasury_tokens.BAL)
    aura = vault.contract(r.treasury_tokens.AURA)
    auraBAL = vault.contract(r.treasury_tokens.AURABAL)
    badgerwbtc_bpt = vault.contract(BADGER80WBTC20)
    badgerreth_bpt = vault.contract(BADGER50RETH50)
    wbtcdigggrav_bpt = vault.contract(WBTC40DIGG40GRAVI20)

    badgerwbtc_rewards = vault.contract(BADGER80WBTC20_AURA)
    badgerreth_rewards = vault.contract(BADGER50RETH50_AURA)
    wbtcdigggrav_rewards = vault.contract(WBTC40DIGG40GRAVI20_AURA)

    # # snaps
    tokens = [bal, aura, auraBAL]
    vault.take_snapshot(tokens)

    # Withdraw all from positions
    badgerwbtc_bpt_bal = badgerwbtc_bpt.balanceOf(vault)
    badgerreth_bpt_bal = badgerreth_bpt.balanceOf(vault)
    wbtcdigggrav_bpt_bal = wbtcdigggrav_bpt.balanceOf(vault)

    badgerwbtc_bpt_staked_bal = badgerwbtc_rewards.balanceOf(vault)
    badgerreth_bpt_staked_bal = badgerreth_rewards.balanceOf(vault)
    wbtcdigggrav_bpt_staked_bal = wbtcdigggrav_rewards.balanceOf(vault)

    badgerwbtc_rewards.withdrawAllAndUnwrap(True)
    badgerreth_rewards.withdrawAllAndUnwrap(True)
    wbtcdigggrav_rewards.withdrawAllAndUnwrap(True)

    assert (
        badgerwbtc_bpt_staked_bal
        == badgerwbtc_bpt.balanceOf(vault) - badgerwbtc_bpt_bal
    )
    assert (
        badgerreth_bpt_staked_bal
        == badgerreth_bpt.balanceOf(vault) - badgerreth_bpt_bal
    )
    assert (
        wbtcdigggrav_bpt_staked_bal
        == wbtcdigggrav_bpt.balanceOf(vault) - wbtcdigggrav_bpt_bal
    )

    vault.post_safe_tx(gen_tenderly=False)


def withdraw_to_vaults():
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)

    # Withdraw Aura strat's assets to the vaults (earn must be stopped)
    for vault_id in AURA_VAULTS:
        vault_address = r.sett_vaults[vault_id]
        vault = safe.contract(vault_address)
        strat = Contract.from_explorer(vault.strategy(), owner=safe.account)
        want = safe.contract(vault.token())

        bal_before = want.balanceOf(vault)

        # Harvest strat
        strat.harvest()

        strat_bal = strat.balanceOf()

        # withdraw to vault
        vault.withdrawToVault()

        assert want.balanceOf(vault) == bal_before + strat_bal
        assert strat.balanceOf() == 0

    safe.post_safe_tx(gen_tenderly=False)
