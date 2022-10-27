from pycoingecko import CoinGeckoAPI

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

SEED_PER_TOKEN_IN_DOLLAR = 1_000_000


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_balancer()
    vault.init_aura()

    # tokens and pool involved
    badger = vault.contract(r.treasury_tokens.BADGER)
    weth = vault.contract(r.treasury_tokens.WETH)
    reth = vault.contract(r.treasury_tokens.RETH)
    bpt_pool_seed = vault.contract(r.balancer.B_50_BADGER_50_RETH)
    bpt_pool_swap = vault.contract(r.balancer.B_50_WETH_50_RETH)

    # snap
    vault.take_snapshot(tokens=[badger, weth])

    # 1. calc needed amounts 1m each token
    ids = ["badger-dao", "weth"]
    prices = CoinGeckoAPI().get_price(ids, "usd")

    badger_price = prices["badger-dao"]["usd"]
    weth_price = prices["weth"]["usd"]

    badger_mantissa = int((SEED_PER_TOKEN_IN_DOLLAR / badger_price) * 1e18)
    weth_mantissa = int((SEED_PER_TOKEN_IN_DOLLAR / weth_price) * 1e18 / 0.98)

    # 2. get reth via balancer swap
    vault.balancer.swap(weth, reth, weth_mantissa, pool=bpt_pool_swap)

    reth_mantissa = int(reth.balanceOf(vault) * 0.98) # dusty

    # print to cross-check: mantissas
    print(
        "[badger_mantissa, reth_mantissa]",
        f"[{badger_mantissa}, {reth_mantissa}]",
    )

    # 3. seed target pool
    vault.balancer.deposit_and_stake(
        [badger, reth],
        [badger_mantissa, reth_mantissa],
        pool=bpt_pool_seed,
        stake=False,
        pool_type="non_stable",
    )

    # 4. stake in AURA
    rewards_contract = vault.contract(vault.aura.get_pool_info(bpt_pool_seed)[3])
    bpt_bal = bpt_pool_seed.balanceOf(vault)
    vault.aura.deposit_all_and_stake(bpt_pool_seed)
    assert rewards_contract.balanceOf(vault) == bpt_bal

    vault.post_safe_tx()
