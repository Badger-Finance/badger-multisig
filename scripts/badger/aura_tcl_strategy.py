from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

console = Console()

# flag
prod = False

# slippages
SLIPPAGE = 0.995
COEF = 0.9825


def main():
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

    # contracts
    vlAURA = vault.contract(r.aura.vlAURA)
    aurabal_rewards = vault.contract(r.aura.aurabal_rewards)

    # snaps
    tokens = [usdc, bal, weth, aura, auraBAL, bauraBal, graviaura]
    vault.take_snapshot(tokens)
    voter.take_snapshot(tokens)

    # 1. claim rewards
    vault.aura.claim_all_from_booster()

    # 2. organised splits for each asset
    balance_bal = bal.balanceOf(vault)
    balance_aura = aura.balanceOf(vault)
    console.print(
        f"[green] === Claimed rewards {balance_bal/1e18} BAL and {balance_aura/1e18} AURA === [/green]"
    )

    # 2.1 swap rewards for usdc
    vault.cow.market_sell(bal, usdc, balance_bal, deadline=60 * 60 * 4, coef=COEF)

    # 2.2 send to voter and deposit into aurabal/bauraBAL
    aura.approve(vlAURA, balance_aura)
    vlAURA.lock(voter, balance_aura)

    voter.print_snapshot()
    vault.post_safe_tx()
