from great_ape_safe import GreatApeSafe
from helpers.addresses import r

LOWER_RANGE_MULTIPLIER = 0.9
UPPER_RANGE_MULTIPLIER = 2
GTC_SELL_PCT = 0.145


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_uni_v3()

    gtc = vault.contract(r.treasury_tokens.GTC)
    weth = vault.contract(r.treasury_tokens.WETH)

    vault.take_snapshot(tokens=[gtc, weth])

    sell_amount = int(gtc.balanceOf(vault) * GTC_SELL_PCT)
    vault.uni_v3.swap([gtc, weth], sell_amount)
    vault.print_snapshot()

    # hardcoded path else it will use the 1% fee pool with different rate
    multihop_path = [gtc.address, 3000, weth.address]

    gtc_rate = vault.uni_v3.get_amount_out(
        [gtc, weth], 1e18, multihop_path=multihop_path
    )

    range_0 = gtc_rate * LOWER_RANGE_MULTIPLIER / 1e18
    range_1 = gtc_rate * UPPER_RANGE_MULTIPLIER / 1e18

    vault.uni_v3.mint_position(
        r.uniswap.v3pool_eth_gtc,
        range_0,
        range_1,
        weth.balanceOf(vault) * 0.98,
        gtc.balanceOf(vault) * 0.98,
    )

    vault.print_snapshot()
    vault.post_safe_tx()
