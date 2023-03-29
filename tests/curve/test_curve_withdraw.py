import pytest


@pytest.fixture(autouse=True)
def deposited(curve, threepool_lptoken, dai, USDC):
    amount_dai = 10_000 * 10 ** dai.decimals()
    amount_usdc = 10_000 * 10 ** USDC.decimals()
    amounts = [amount_dai, amount_usdc, 0]
    curve.deposit(threepool_lptoken, amounts)


def test_withdraw(safe, curve, registry, threepool_lptoken):
    pool_addr = registry.pool_list(0)
    true_length = registry.get_n_coins(pool_addr)[0]

    # Get list of token addresses in pool
    coins = list(registry.get_coins(pool_addr))[:true_length]

    # get safe balance of each token
    before_coin_balances = [safe.contract(coin).balanceOf(safe) for coin in coins]

    amount = threepool_lptoken.balanceOf(safe)
    curve.withdraw(threepool_lptoken, amount)

    after_coin_balances = [safe.contract(coin).balanceOf(safe) for coin in coins]

    # Tokens are withdrawn in unknown proportions, compare sum of token balances from before
    assert sum(after_coin_balances) > sum(before_coin_balances)


def test_withdraw_tricrypto(safe, curve, tricrypto_lptoken):
    coins = curve._get_coins(tricrypto_lptoken)

    before_coin_balances = [safe.contract(coin).balanceOf(safe) for coin in coins]
    amount = tricrypto_lptoken.balanceOf(safe)

    curve.withdraw(tricrypto_lptoken, amount)

    after_coin_balances = [safe.contract(coin).balanceOf(safe) for coin in coins]

    assert sum(after_coin_balances) > sum(before_coin_balances)


def test_withdraw_one_coin(safe, curve, threepool_lptoken, USDC):
    before_bal_usdc = USDC.balanceOf(safe)

    amount = threepool_lptoken.balanceOf(safe)
    curve.withdraw_to_one_coin(threepool_lptoken, amount, USDC)

    assert USDC.balanceOf(safe) > before_bal_usdc
