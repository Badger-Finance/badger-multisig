from brownie import interface, chain, accounts
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from rich.console import Console
from helpers.constants import AddressZero

C = Console()

AURABAL_STRAT_CURRENT = registry.eth.strategies._deprecated["native.bauraBal"]["v1.1"]
AURABAL_STRAT_NEW = registry.eth.strategies["native.bauraBal"]
BAURA_BAL = registry.eth.sett_vaults.bauraBal
DEV_MULTI = registry.eth.badger_wallets.dev_multisig
BADGERTREE = registry.eth.badger_wallets.badgertree
TROPS = registry.eth.badger_wallets.treasury_ops_multisig

USER = "0xf18da2faba96793f02264d1a047790002f32010f"


def main(simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    auraBal_strat_current = interface.IAuraBalStaker(
        AURABAL_STRAT_CURRENT, owner=safe.account
    )
    auraBal_strat_new = interface.IAuraBalStaker(AURABAL_STRAT_NEW, owner=safe.account)
    auraBal_vault = interface.ITheVault(BAURA_BAL, owner=safe.account)
    want = interface.IERC20(auraBal_vault.token())
    bb_a_usd = interface.IERC20(auraBal_strat_new.BB_A_USD())

    aura = interface.IERC20(auraBal_strat_new.AURA())
    bal = interface.IERC20(auraBal_strat_new.BAL())
    graviaura = interface.IERC20(auraBal_strat_new.GRAVIAURA())

    ## Check integrity
    assert auraBal_vault.strategy() == auraBal_strat_current.address

    assert auraBal_strat_new.want() == auraBal_strat_current.want()
    assert auraBal_strat_new.vault() == auraBal_strat_current.vault()
    assert (
        auraBal_strat_new.withdrawalMaxDeviationThreshold()
        == auraBal_strat_current.withdrawalMaxDeviationThreshold()
    )
    assert (
        auraBal_strat_new.autoCompoundRatio()
        == auraBal_strat_current.autoCompoundRatio()
    )
    assert (
        auraBal_strat_new.claimRewardsOnWithdrawAll()
        == auraBal_strat_current.claimRewardsOnWithdrawAll()
    )
    assert (
        auraBal_strat_new.balEthBptToAuraBalMinOutBps()
        == auraBal_strat_current.balEthBptToAuraBalMinOutBps()
    )
    # New variables
    assert auraBal_strat_new.BB_A_USD() != AddressZero
    assert auraBal_strat_new.minBbaUsdHarvest() == int(1000e18)

    ## Harvest current strat
    tx = auraBal_strat_current.harvest()
    assert len(tx.events["TreeDistribution"]) == 2  # GraviAURA and bBB-A-USD
    # Ensure that no assets remain sitting on strategy
    assert bb_a_usd.balanceOf(auraBal_strat_current) == 0
    assert aura.balanceOf(auraBal_strat_current) == 0
    assert want.balanceOf(auraBal_strat_current) == 0
    assert bal.balanceOf(auraBal_strat_current) == 0
    assert graviaura.balanceOf(auraBal_strat_current) == 0

    ## withdrawToVault
    prev_strat_balance = (
        auraBal_strat_current.balanceOf()
    )  # balanceOfWant().add(balanceOfPool());
    prev_vault_balance = want.balanceOf(BAURA_BAL)
    auraBal_vault.withdrawToVault()
    assert want.balanceOf(BAURA_BAL) == prev_strat_balance + prev_vault_balance
    assert auraBal_strat_current.balanceOf() == 0

    # setStrategy
    assert auraBal_strat_current.want() == auraBal_strat_new.want()  # Confirm strategy
    auraBal_vault.setStrategy(AURABAL_STRAT_NEW)
    assert auraBal_vault.strategy() == auraBal_strat_new.address

    # Earn to new strat
    prev_available = auraBal_vault.available()
    prev_strat_balance = auraBal_strat_new.balanceOf()
    auraBal_vault.earn()
    assert auraBal_strat_new.balanceOf() == prev_available + prev_strat_balance

    # Run a few test actions
    if simulation == "true":
        chain.sleep(13 * 100)
        chain.mine()

        # Harvest
        tx = auraBal_strat_new.harvest()
        assert (
            len(tx.events["TreeDistribution"]) == 1
        )  # graviAURA (No bBB_A_USD anymore)
        assert bb_a_usd.balanceOf(AURABAL_STRAT_NEW) > 0  # With

        chain.sleep(13 * 100)
        chain.mine()

        # Withdraw
        user = accounts.at(USER, force=True)
        prev_user_balance = want.balanceOf(USER)
        auraBal_vault.withdrawAll({"from": user})
        assert want.balanceOf(USER) > prev_user_balance

        chain.sleep(13 * 100)
        chain.mine()

        # Harvest with min threshold for USD set to 0
        auraBal_strat_new.setMinBbaUsdHarvest(0)
        assert auraBal_strat_new.minBbaUsdHarvest() == 0

        tx = auraBal_strat_new.harvest()
        assert bb_a_usd.balanceOf(AURABAL_STRAT_NEW) == 0  # All bb-a-usd gets processed

        C.print("[green]Simulation successful![/green]")
    else:
        safe.post_safe_tx()
