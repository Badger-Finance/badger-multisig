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
SLIPPAGE = 0.995
COEF = 0.98


def main(aura_pct_lock="0.7"):
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

    # 1. claim rewards
    if claim_aura_rewards:
        balance_bal_before = bal.balanceOf(vault)
        balance_aura_before = aura.balanceOf(vault)
        vault.aura.claim_all_from_booster()

        # 2. organised splits for each asset
        balance_bal = bal.balanceOf(vault)
        balance_aura = aura.balanceOf(vault)
        console.print(
            f"[green] === Claimed rewards {(balance_bal-balance_bal_before)/1e18} BAL and {(balance_aura-balance_aura_before)/1e18} AURA === [/green]"
        )

        # 2.1 send to voter and deposit into aurabal/bauraBAL
        aura.approve(vlAURA, balance_aura * float(aura_pct_lock))
        vlAURA.lock(voter, balance_aura * float(aura_pct_lock))

    # 2.2 swap rewards for usdc
    if aura.balanceOf(vault) > 0:
        vault.cow.market_sell(
            aura, usdc, aura.balanceOf(vault), deadline=60 * 60 * 4, coef=COEF
        )

    if bal.balanceOf(vault) > 0:
        vault.cow.market_sell(
            bal, usdc, bal.balanceOf(vault), deadline=60 * 60 * 4, coef=COEF
        )

    if claim_uni_v3_fees:
        vault.init_uni_v3()
        vault.uni_v3.collect_fees()

    if sweep_bvecvx:
        bvecxv.transfer(voter, bvecxv.balanceOf(vault))

    voter.print_snapshot()
    vault.post_safe_tx()
