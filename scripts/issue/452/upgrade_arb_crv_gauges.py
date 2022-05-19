from decimal import Decimal

from brownie import accounts, web3, interface, chain
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ARBITRUM
from helpers.addresses import registry

console = Console()

DEV_MULTI = registry.arbitrum.badger_wallets.dev_multisig
PROXY_ADMIN = registry.arbitrum.proxyAdminDev
CRV = registry.arbitrum.treasury_tokens.CRV
TRICRYPTO_STRATEGY = ADDRESSES_ARBITRUM["strategies"]["native.tricrypto"]
RENCRV_STRATEGY = ADDRESSES_ARBITRUM["strategies"]["native.renCrv"]

RENCRV_LOGIC = ADDRESSES_ARBITRUM["logic"]["native.renCrv_v2"]
TRICRYPTO_LOGIC = ADDRESSES_ARBITRUM["logic"]["native.tricrypto_v2"]

GAUGE_FACTORY = "0xabC000d88f23Bb45525E447528DBF656A9D55bf5"
TRICRYPTO_GAUGE = "0x555766f3da968ecBefa690Ffd49A2Ac02f47aa5f"
RENCRV_GAUGE = "0xDB3fd1bfC67b5D4325cb31C04E0Cae52f1787FD6"


def main(simulation=True):
    safe = GreatApeSafe(DEV_MULTI)

    console.print(
        f"[green]Updating Tricrypto strategy logic to {TRICRYPTO_LOGIC}[/green]"
    )
    upgrade_strategy_logic(
        TRICRYPTO_STRATEGY,
        TRICRYPTO_LOGIC,
        TRICRYPTO_GAUGE,
        GAUGE_FACTORY,
        safe,
        simulation,
    )

    console.print(f"[green]Updating Rencrv strategy logic to {RENCRV_LOGIC}[/green]")
    upgrade_strategy_logic(
        RENCRV_STRATEGY, RENCRV_LOGIC, RENCRV_GAUGE, GAUGE_FACTORY, safe, simulation
    )

    safe.post_safe_tx(call_trace=True)


def upgrade_strategy_logic(
    proxy_address: str,
    logic_address: str,
    gauge_address: str,
    gauge_factory_address: str,
    safe: GreatApeSafe,
    simulation: bool = True,
):
    proxy_admin = interface.IProxyAdmin(PROXY_ADMIN, owner=safe.account)
    strat_proxy = interface.ICrvStrategy(proxy_address, owner=safe.account)

    prev_strategist = strat_proxy.strategist()
    prev_controller = strat_proxy.controller()
    prev_gov = strat_proxy.governance()
    prev_guardian = strat_proxy.guardian()
    prev_keeper = strat_proxy.keeper()
    prev_perFeeG = strat_proxy.performanceFeeGovernance()
    prev_perFeeS = strat_proxy.performanceFeeStrategist()
    prev_reward = strat_proxy.reward()
    prev_unit = strat_proxy.uniswap()
    prev_gauge = strat_proxy.gauge()
    prev_swapr_router = strat_proxy.SWAPR_ROUTER()

    proxy_admin.upgrade(proxy_address, logic_address)

    strat_proxy.setGauge(gauge_address)
    strat_proxy.setGaugeFactory(gauge_factory_address)

    assert prev_strategist == strat_proxy.strategist()
    assert prev_controller == strat_proxy.controller()
    assert prev_gov == strat_proxy.governance()
    assert prev_guardian == strat_proxy.guardian()
    assert prev_keeper == strat_proxy.keeper()
    assert prev_perFeeG == strat_proxy.performanceFeeGovernance()
    assert prev_perFeeS == strat_proxy.performanceFeeStrategist()
    assert prev_reward == strat_proxy.reward()
    assert prev_unit == strat_proxy.uniswap()
    assert prev_swapr_router == strat_proxy.SWAPR_ROUTER()
    assert gauge_address == strat_proxy.gauge()
    assert gauge_factory_address == strat_proxy.gaugeFactory()

    if simulation:
        gauge = interface.ICurveGauge(gauge_address)

        # sleep one day to accrue more crv
        chain.sleep(86400)
        chain.mine()

        balance_before = gauge.balanceOf(proxy_address)

        # harvest
        strat_proxy.harvest()

        balance_after = gauge.balanceOf(proxy_address)

        assert balance_after > balance_before
