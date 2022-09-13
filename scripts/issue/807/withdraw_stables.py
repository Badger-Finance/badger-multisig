from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_aave()
    vault.init_compound()
    vault.init_convex()
    vault.init_aura()
    vault.init_balancer()
    vault.init_curve()
    vault.init_sushi()

    usdt = vault.contract(r.treasury_tokens.USDT)
    usdc = vault.contract(r.treasury_tokens.USDC)
    fei = vault.contract(r.treasury_tokens.FEI)
    frax = interface.ERC20(r.treasury_tokens.FRAX, owner=vault.account)
    dai = vault.contract(r.treasury_tokens.DAI)

    fxs = interface.ERC20(r.treasury_tokens.FXS, owner=vault.account)
    comp = vault.contract(r.treasury_tokens.COMP)
    weth = vault.contract(r.treasury_tokens.WETH)

    cDAI = vault.contract(r.treasury_tokens.cDAI)
    bpt_3pool = vault.contract(r.balancer.B_3POOL)

    aave_stables = [usdt, usdc, fei, frax]
    a_stables = [
        vault.contract(r.treasury_tokens[f"a{token.symbol()}"])
        for token in aave_stables
    ]

    vault.take_snapshot(
        tokens=aave_stables + a_stables + [dai, fxs, comp, cDAI, bpt_3pool]
    )

    # CONVEX
    # https://etherscan.io/tx/0xa084e77b26cae597bd973c3ab91b3045b7fa873d13cbcc48ac58231a3230f756#eventlog (#189)
    kek_id = "0377F3E93D8BCB691D20E708122E8F9AFD168512D033F5738EB8CF72862E1090"
    # withdraw -> afrax
    vault.convex.withdraw_locked(a_stables[-1], kek_id)

    # AAVE
    # withdraw -> usdt, usdc, fei, frax
    for token in aave_stables:
        vault.aave.withdraw_all(token)

    # COMPOUND
    # withdraw -> dai
    vault.compound.withdraw_ctoken(cDAI, cDAI.balanceOf(vault))
    # claim -> COMP
    vault.compound.claim_all()

    # AURA/BALANCER
    # withdraw -> staBAL3
    vault.aura.unstake_all_and_withdraw_all(bpt_3pool)
    # withdraw -> usdc, dai, usdt
    vault.balancer.unstake_all_and_withdraw_all([usdc, dai, usdt], pool=bpt_3pool)

    # roughly 2:2:2:1:1 USDT:USDC:DAI:FRAX:FEI at this point

    # target: 1:1:1 USDT:USDC:DAI
    frax_portion = frax.balanceOf(vault) * 2 / 3
    fei_portion = fei.balanceOf(vault) * 2 / 3

    vault.curve.swap(frax, dai, frax_portion)
    vault.curve.swap(fei, usdc, fei_portion)

    left_over_frax = frax.balanceOf(vault)
    left_over_fei = fei.balanceOf(vault)

    vault.curve.swap(frax, usdt, left_over_frax)
    vault.curve.swap(fei, usdt, left_over_fei)

    # sell rewards to lowest balance token of the 3
    lowest_bal_token = min([usdt, usdc, dai], key=lambda token: token.balanceOf(vault))

    vault.sushi.swap_tokens_for_tokens(
        fxs, fxs.balanceOf(vault), [fxs, weth, lowest_bal_token]
    )
    vault.sushi.swap_tokens_for_tokens(
        comp, comp.balanceOf(vault), [comp, weth, lowest_bal_token]
    )

    vault.print_snapshot()
    vault.post_safe_tx()
