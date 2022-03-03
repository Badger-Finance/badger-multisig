from brownie import Contract, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


DUSTY = .998


def main():
    """
    send all of treasury vault's $3pool to work on the convex 3eur farm.
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    safe.init_curve()
    safe.init_convex()

    balance_checker = interface.IBalanceChecker(
        registry.eth.helpers.balance_checker, owner=safe.account
    )

    threepool = interface.ICurveLP(
        registry.eth.treasury_tokens.crv3pool, owner=safe.account
    )
    # TODO: IStableSwap3Pool doesnt have name attr???
    three_eur = Contract.from_explorer( #interface.IStableSwap3Pool(
        registry.eth.treasury_tokens.crv3eur, owner=safe.account
    )
    usdc = interface.ERC20(
        registry.eth.treasury_tokens.USDC, owner=safe.account
    )
    eurs = interface.ERC20(
        registry.eth.treasury_tokens.EURS, owner=safe.account
    )

    safe.take_snapshot(tokens=[
        threepool.address, three_eur.address, usdc.address, eurs.address
    ])

    bal_threepool = threepool.balanceOf(safe)

    safe.curve.withdraw_to_one_coin(threepool, bal_threepool, usdc)
    safe.curve.swap(usdc, eurs, usdc.balanceOf(safe) * DUSTY)
    safe.curve.deposit(three_eur, eurs.balanceOf(safe) * DUSTY, eurs)
    safe.convex.deposit_all_and_stake(three_eur)

    # confirm staked balance onchain
    _, _, _, rewards = safe.convex.get_pool_info(three_eur)
    # rough expectation; covert usd -> eur and allow 1% fee and slippage
    expected = bal_threepool / 1.17 * .99
    balance_checker.verifyBalance(rewards, safe, expected)

    # skipping preview; getting timeout of 10s here, probably from
    # `File "web3/eth.py", line 735, in estimate_gas`
    safe.post_safe_tx(skip_preview=True)
