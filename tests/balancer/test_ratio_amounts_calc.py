from great_ape_safe.ape_api.helpers.coingecko import get_cg_price
import pytest


def test_bpt_ratio_amounts_wbtc_badger(balancer, wbtc, badger, badger_bpt):
    # 20% wbtc, 80% badger
    usd_amount = 10_000
    wbtc_portion = usd_amount * 0.2
    badger_portion = usd_amount * 0.8

    wbtc_amount, badger_amount = balancer.bpt_ratio_amounts(
        badger_bpt, [wbtc, badger], usd_amount
    )

    assert get_cg_price(wbtc.address) * wbtc_amount / 1e8 == pytest.approx(
        wbtc_portion, 1
    )
    assert get_cg_price(badger.address) * badger_amount / 1e18 == pytest.approx(
        badger_portion * 0.8, 1
    )


def test_bpt_ratio_amounts_weth_dai(balancer, weth, dai, weighted_bpt):
    # 60 weth/40 dai
    usd_amount = 10_000
    weth_portion = usd_amount * 0.6
    dai_portion = usd_amount * 0.4

    dai_amount, weth_amount = balancer.bpt_ratio_amounts(
        weighted_bpt, [weth, dai], usd_amount
    )

    assert get_cg_price(weth.address) * weth_amount / 1e18 == pytest.approx(
        weth_portion, 1
    )
    assert get_cg_price(dai.address) * dai_amount / 1e18 == pytest.approx(
        dai_portion, 1
    )


def test_bpt_ratio_amounts_threepool(balancer, dai, USDC, usdt, threepool_bpt):
    usd_amount = 10_000
    dai_portion = usd_amount * 1 / 3
    usdc_portion = usd_amount * 1 / 3
    usdt_portion = usd_amount * 1 / 3

    dai_amount, usdc_amount, usdt_amount = balancer.bpt_ratio_amounts(
        threepool_bpt, [dai, USDC, usdt], usd_amount
    )

    assert get_cg_price(dai.address) * dai_amount / 1e18 == pytest.approx(
        dai_portion, 1
    )
    assert get_cg_price(USDC.address) * usdc_amount / 1e6 == pytest.approx(
        usdc_portion, 1
    )
    assert get_cg_price(usdt.address) * usdt_amount / 1e6 == pytest.approx(
        usdt_portion, 1
    )
