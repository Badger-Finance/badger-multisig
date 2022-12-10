from rich.console import Console
from great_ape_safe import GreatApeSafe
from helpers.addresses import r

console = Console()

BADGER80WBTC20 = r.balancer.B_20_BTC_80_BADGER
BADGER50RETH50 = r.balancer.B_50_BADGER_50_RETH
WBTC40DIGG40GRAVI20 = r.balancer.bpt_40wbtc_40digg_20graviaura

def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_aura()

    bal = vault.contract(r.treasury_tokens.BAL)
    aura = vault.contract(r.treasury_tokens.AURA)
    auraBAL = vault.contract(r.treasury_tokens.AURABAL)
    badgerwbtc_bpt = vault.contract(BADGER80WBTC20)
    badgerreth_bpt = vault.contract(BADGER50RETH50)
    wbtcdigggrav_bpt = vault.contract(WBTC40DIGG40GRAVI20)

    # snaps
    tokens = [bal, aura, auraBAL]
    vault.take_snapshot(tokens)

    # Claim all accrued rewards
    vault.aura.claim_all_from_booster()

    # Withdraw all from positions
    vault.aura.withdraw_all(badgerwbtc_bpt)
    vault.aura.withdraw_all(badgerreth_bpt)
    vault.aura.withdraw_all(wbtcdigggrav_bpt)

    vault.post_safe_tx()