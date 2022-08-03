from brownie import ZERO_ADDRESS, interface
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

console = Console()

# flag
prod = False

# slippages
SLIPPAGE = 0.995
COEF = 0.9825

# breakdowns of rewards
AURA_FOR_STABLES = 0.3
BAL_FOR_STABLES = 0.7


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
    b80bal_20weth = vault.contract(r.balancer.B_80_BAL_20_WETH)
    bauraBAL_stable = vault.contract(r.balancer.B_auraBAL_STABLE)
    auraBAL = vault.contract(r.treasury_tokens.AURABAL)
    bauraBal = vault.contract(r.sett_vaults.bauraBal)
    graviaura = vault.contract(r.sett_vaults.graviAURA)
    bvecvx = vault.contract(r.sett_vaults.bveCVX)
    bcvxcrv = vault.contract(r.sett_vaults.bcvxCRV)

    # contracts
    wrapper = vault.contract(r.aura.wrapper)
    registry_v_2 = vault.contract(r.registry_v2, interface.IBadgerRegistryV2)

    # snaps
    vault.take_snapshot([usdc, auraBAL, bauraBal, graviaura])
    voter.take_snapshot([aura])

    # 1. claim rewards
    vault.aura.claim_all_from_booster()

    # 2. organised splits for each asset
    balance_bal = bal.balanceOf(vault)
    balance_aura = aura.balanceOf(vault)
    console.print(
        f"[green] === Claimed rewards {balance_bal/1e18} BAL and {balance_aura/1e18} AURA === [/green]"
    )

    bal_swap_for_usdc = balance_bal * BAL_FOR_STABLES
    aura_swap_for_usdc = balance_aura * AURA_FOR_STABLES

    # 2.1 swap rewards for usdc
    vault.cow.market_sell(bal, usdc, bal_swap_for_usdc, deadline=60 * 60 * 4, coef=COEF)
    vault.cow.market_sell(
        aura, usdc, aura_swap_for_usdc, deadline=60 * 60 * 4, coef=COEF
    )

    # 2.2 send to voter and deposit into aurabal/bauraBAL
    aura.transfer(voter, balance_aura - aura_swap_for_usdc)

    bal_to_deposit = balance_bal - bal_swap_for_usdc

    # wrapper min estimation
    wrapper_aurabal_out = wrapper.getMinOut(bal_to_deposit, 9950)

    # bpt out and swap estimation
    bpt_out = vault.balancer.get_amount_bpt_out(
        [bal, weth], [bal_to_deposit, 0], pool=b80bal_20weth
    ) * SLIPPAGE
    amt_pool_swapped_out = vault.balancer.get_amount_out(
        b80bal_20weth, auraBAL, bpt_out, pool=bauraBAL_stable
    ) * SLIPPAGE

    if amt_pool_swapped_out > wrapper_aurabal_out:
        console.print(
            "[green] === INFO: better outcome of auraBAL via depositing and swapping === [/green]"
        )
        console.print(
            f"[green] === Extra {(amt_pool_swapped_out-wrapper_aurabal_out)/1e18} auraBAL received === [/green]"
        )
        vault.balancer.deposit_and_stake(
            [bal, weth], [bal_to_deposit, 0], pool=b80bal_20weth, stake=False
        )
        balance_bpt = b80bal_20weth.balanceOf(vault) * SLIPPAGE
        vault.balancer.swap(b80bal_20weth, auraBAL, balance_bpt, pool=bauraBAL_stable)
    else:
        console.print(
            "[green] === INFO: better outcome of auraBAL via wrapper === [/green]"
        )
        console.print(
            f"[green] === Extra {(wrapper_aurabal_out - amt_pool_swapped_out)/1e18} auraBAL received === [/green]"
        )
        bal.approve(wrapper, bal_to_deposit)
        wrapper.deposit(
            bal_to_deposit,  # uint256 _amount
            wrapper_aurabal_out,  # uint256 _minOut
            False,  # bool _lock
            ZERO_ADDRESS,  # address _stakeAddress
        )

    # 3. dogfood in bauraBAL if in prod
    vault_status = registry_v_2.productionVaultInfoByVault(bauraBal)[2]
    # check if vault is `open`, then dogfood
    if vault_status == 3:
        auraBAL.approve(bauraBal, 2 ** 256 - 1)
        bauraBal.depositAll()
        auraBAL.approve(bauraBal, 0)

    # 3. tree claim
    if bauraBal.balanceOf(vault) > 0:
        vault.init_badger()
        # will claim: bcvxCRV, bveCVX & graviAURA
        # NOTE: should we just narrow the claim for graviAURA and modify `claim_all`?
        # NOTE: short <2h window for signing as new cycles may be posted
        vault.badger.claim_all()

        # 3.1: send to tree for deficit coverage over time.
        # will help together with the post-thresher trasnfer
        bcvxcrv.transfer(r.badger_wallets.badgertree, bcvxcrv.balanceOf(vault))

        # 3.2: send influence asset to voter
        bvecvx.trasnfer(voter, bvecvx.balanceOf(vault))

    voter.print_snapshot()
    vault.post_safe_tx()
