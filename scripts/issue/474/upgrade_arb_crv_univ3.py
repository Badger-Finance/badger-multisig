from decimal import Decimal

from brownie import accounts, web3, interface, chain
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ARBITRUM
from helpers.addresses import registry

console = Console()

DEV_MULTI = registry.arbitrum.badger_wallets.dev_multisig
PROXY_ADMIN = registry.arbitrum.proxyAdminDev

TRICRYPTO_STRATEGY = ADDRESSES_ARBITRUM["strategies"]["native.tricrypto"]
TRICRYPTO_LOGIC = ADDRESSES_ARBITRUM["logic"]["native.tricrypto"]
TRICRYPTO_VAULT = ADDRESSES_ARBITRUM["sett_vaults"]["bcrvTricrypto"]

RENCRV_STRATEGY = ADDRESSES_ARBITRUM["strategies"]["native.renCrv"]
RENCRV_LOGIC = ADDRESSES_ARBITRUM["logic"]["native.renCrv"]
RENCRV_VAULT = ADDRESSES_ARBITRUM["sett_vaults"]["bcrvRenBTC"]

UNIV3_ROUTER = "0xE592427A0AEce92De3Edee1F18E0157C05861564"


def main(simulation=True):
    safe = GreatApeSafe(DEV_MULTI)

    console.print(
        f"Updating Tricrypto strategy logic to {TRICRYPTO_LOGIC}"
    )
    upgrade_strategy_logic(
        TRICRYPTO_STRATEGY,
        TRICRYPTO_LOGIC,
        TRICRYPTO_VAULT,
        safe,
        simulation,
    )

    console.print(f"Updating Rencrv strategy logic to {RENCRV_LOGIC}")
    upgrade_strategy_logic(
        RENCRV_STRATEGY, RENCRV_LOGIC, RENCRV_VAULT, safe, simulation
    )

    safe.post_safe_tx(call_trace=True)


def upgrade_strategy_logic(
    strategy_proxy_address: str,
    logic_address: str,
    vault_proxy_address: str,
    safe: GreatApeSafe,
    simulation: bool = True,
):
    vault = interface.ITheVault(vault_proxy_address, owner=safe.account)
    proxy_admin = interface.IProxyAdmin(PROXY_ADMIN, owner=safe.account)
    strat_proxy = interface.ICrvStrategy(strategy_proxy_address, owner=safe.account)
    controller_proxy = interface.IController(strat_proxy.controller(), owner=vault)

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
    prev_gauge_factory = strat_proxy.gaugeFactory()
    prev_swapr_router = strat_proxy.SWAPR_ROUTER()

    if simulation:
        # Harvest to clear any pending rewards for fresh test case
        gauge = strat_proxy.gauge()
        strat_proxy.harvest()

        # Harvest on old strat, store gain in want
        want = interface.IERC20(gauge)
        prev_want_bal = want.balanceOf(strat_proxy.address)

        chain.sleep(60*60*2)
        chain.mine()

        strat_proxy.harvest()

        after_want_bal = want.balanceOf(strat_proxy.address)
        old_path_want_gain = after_want_bal - prev_want_bal

        # Withdraw want change to keep same conditions for future test
        controller_proxy.withdraw(vault.token(), old_path_want_gain)
        assert want.balanceOf(strat_proxy.address) == prev_want_bal

    proxy_admin.upgrade(strategy_proxy_address, logic_address)

    strat_proxy.setUniV3Allowance()

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
    assert prev_gauge == strat_proxy.gauge()
    assert prev_gauge_factory == strat_proxy.gaugeFactory()
    assert UNIV3_ROUTER == strat_proxy.UNIV3_ROUTER()

    if simulation:
        # Harvest on new strat, store gain in want, compare to prev swap (should be more efficient)
        prev_want_bal = want.balanceOf(strat_proxy.address)

        chain.sleep(60*60*2)
        chain.mine()
        
        strat_proxy.harvest()

        after_want_bal = want.balanceOf(strat_proxy.address)
        new_path_want_gain = after_want_bal - prev_want_bal

        console.print(f"Old want gain: {old_path_want_gain}")
        console.print(f"New want gain: {new_path_want_gain}")

        # Compare
        assert new_path_want_gain >= old_path_want_gain
