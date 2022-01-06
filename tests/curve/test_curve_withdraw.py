import pytest


@pytest.fixture(scope='function', autouse=True)
def deposited(curve, tripool_lptoken, USDC, safe):
    amount_dai = 10_000 * 10**18
    amount_usdc = 10_000 * 10**USDC.decimals()
    amounts = [amount_dai, amount_usdc, 0]
    curve.deposit(tripool_lptoken, amounts)

def test_withdraw(safe, curve, registry, tripool_lptoken):
    pool_addr =  registry.pool_list(0)
    true_length = registry.get_n_coins(pool_addr)[0]
    
    # Get list of token addresses in pool
    coins = list(registry.get_coins(pool_addr))[:true_length]

    # get safe balance of each token
    before_coin_balances = [safe.contract(coin).balanceOf(safe) for coin in coins]

    amount = tripool_lptoken.balanceOf(safe)
    curve.withdraw(tripool_lptoken, amount)

    after_coin_balances = [safe.contract(coin).balanceOf(safe) for coin in coins]

    # Tokens are withdrawn in unknown proportions, compare sum of token balances from before
    assert sum(after_coin_balances) > sum(before_coin_balances)

def test_withdraw_one_coin(safe, curve, tripool_lptoken, USDC):
    before_bal_usdc = USDC.balanceOf(safe)

    amount = tripool_lptoken.balanceOf(safe)
    curve.withdraw_to_one_coin(tripool_lptoken, amount, USDC)
    
    assert USDC.balanceOf(safe) > before_bal_usdc
  



        