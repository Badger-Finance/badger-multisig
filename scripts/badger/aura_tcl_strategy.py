from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

console = Console()

# flag
prod = False
claim_aura_rewards = True
claim_uni_v3_fees = False
sweep_bvecvx = False

# slippages
COEF = 0.95
DEADLINE = 60 * 60 * 12


def wd_unlocked_aura():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

    aura = voter.contract(r.treasury_tokens.AURA)
    badger = voter.contract(r.treasury_tokens.BADGER)
    vlAURA = voter.contract(r.aura.vlAURA)
    graviaura = voter.contract(r.sett_vaults.graviAURA)

    voter.take_snapshot([aura, badger, graviaura]), vault.take_snapshot([aura, badger])

    if graviaura.balanceOf(voter) > 0:
        graviaura.withdrawAll()

    unlockable = vlAURA.lockedBalances(voter)[1]
    if unlockable > 0:
        relock = False
        vlAURA.processExpiredLocks(relock)

        aura.transfer(vault, aura.balanceOf(voter))

    if badger.balanceOf(voter) > 0:
        badger.transfer(vault, badger.balanceOf(voter))

    vault.print_snapshot()
    voter.post_safe_tx()


def main(aura_pct_lock="0."):
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    vault.init_aura()
    vault.init_balancer()
    vault.init_cow(prod)

    # tokens involved
    usdc = vault.contract(r.treasury_tokens.USDC)
    bal = vault.contract(r.treasury_tokens.BAL)
    weth = vault.contract(r.treasury_tokens.WETH)
    aura = vault.contract(r.treasury_tokens.AURA)
    auraBAL = vault.contract(r.treasury_tokens.AURABAL)
    bauraBal = vault.contract(r.sett_vaults.bauraBal)
    graviaura = vault.contract(r.sett_vaults.graviAURA)
    badger = vault.contract(r.treasury_tokens.BADGER)
    wbtc = vault.contract(r.treasury_tokens.WBTC)
    bvecxv = vault.contract(r.treasury_tokens.bveCVX)

    # contracts
    vlAURA = vault.contract(r.aura.vlAURA)

    # snaps
    tokens = [usdc, bal, weth, aura, auraBAL, bauraBal, graviaura, badger, wbtc, bvecxv]
    vault.take_snapshot(tokens)
    voter.take_snapshot(tokens)

    rewards = [
        r.aura.aura_20wbtc80badger_gauge,
        r.aura.aura_40wbtc40digg20gravi_gauge,
        r.aura.aura_50reth50badger_gauge,
    ]

    # 1. claim rewards
    if claim_aura_rewards:
        balance_bal_before = bal.balanceOf(vault)
        balance_aura_before = aura.balanceOf(vault)
        vault.aura.claim_all_from_booster(rewards)

        # 2. organised splits for each asset
        balance_bal = bal.balanceOf(vault)
        balance_aura = aura.balanceOf(vault)
        console.print(
            f"[green] === Claimed rewards {(balance_bal-balance_bal_before)/1e18} BAL and {(balance_aura-balance_aura_before)/1e18} AURA === [/green]"
        )

        # 2.1 send to voter and deposit into aurabal/bauraBAL
        if float(aura_pct_lock) > 0:
            aura.approve(vlAURA, balance_aura * float(aura_pct_lock))
            vlAURA.lock(voter, balance_aura * float(aura_pct_lock))

    # 2.2 swap rewards for usdc
    if aura.balanceOf(vault) > 0:
        vault.cow.market_sell(
            aura, usdc, aura.balanceOf(vault), deadline=DEADLINE, coef=COEF
        )

    if bal.balanceOf(vault) > 0:
        vault.cow.market_sell(
            bal, usdc, bal.balanceOf(vault), deadline=DEADLINE, coef=COEF
        )

    if claim_uni_v3_fees:
        vault.init_uni_v3()
        vault.uni_v3.collect_fees()

    if sweep_bvecvx:
        bvecxv.transfer(voter, bvecxv.balanceOf(vault))

    voter.print_snapshot()
    vault.post_safe_tx()
