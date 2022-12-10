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

    assert badgerwbtc_bpt_staked_bal == badgerwbtc_bpt.balanceOf(vault) - badgerwbtc_bpt_bal
    assert badgerreth_bpt_staked_bal == badgerreth_bpt.balanceOf(vault) - badgerreth_bpt_bal
    assert wbtcdigggrav_bpt_staked_bal == wbtcdigggrav_bpt.balanceOf(vault) - wbtcdigggrav_bpt_bal

    vault.post_safe_tx(gen_tenderly=False)