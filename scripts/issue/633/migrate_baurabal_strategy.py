from brownie import interface, chain, accounts
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from rich.console import Console

C = Console()

AURABAL_STRAT_CURRENT = registry.eth.strategies._deprecated["native.bauraBal"]
AURABAL_STRAT_NEW = registry.eth.strategies["native.bauraBal"]
BAURA_BAL = registry.eth.sett_vaults.bauraBal
DEV_MULTI = registry.eth.badger_wallets.dev_multisig
BADGERTREE = registry.eth.badger_wallets.badgertree
TROPS = registry.eth.badger_wallets.treasury_ops_multisig

USER = "0xdE0AEf70a7ae324045B7722C903aaaec2ac175F5"


def main(simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    auraBal_strat_current = interface.IAuraBalStaker(
        AURABAL_STRAT_CURRENT, owner=safe.account
    )
    auraBal_strat_new = interface.IAuraBalStaker(AURABAL_STRAT_NEW, owner=safe.account)
    auraBal_vault = interface.ITheVault(BAURA_BAL, owner=safe.account)
    want = interface.IERC20(auraBal_vault.token())
    bb_a_usd = interface.IERC20(auraBal_strat_new.BB_A_USD())

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

    ## Harvest current strat
    prev_bbausd_strat_balance = bb_a_usd.balanceOf(AURABAL_STRAT_CURRENT)
    auraBal_strat_current.harvest()
    assert bb_a_usd.balanceOf(AURABAL_STRAT_CURRENT) > prev_bbausd_strat_balance

    ## Emit all accumulated bb_a_usd on the strat to this point (Will process perf fees)
    prev_bbausd_tree_balance = bb_a_usd.balanceOf(BADGERTREE)
    prev_bbausd_trops_balance = bb_a_usd.balanceOf(TROPS)
    auraBal_vault.emitNonProtectedToken(bb_a_usd.address)
    assert bb_a_usd.balanceOf(BADGERTREE) > prev_bbausd_tree_balance
    assert bb_a_usd.balanceOf(TROPS) > prev_bbausd_trops_balance  # Fees
    assert bb_a_usd.balanceOf(AURABAL_STRAT_CURRENT) == 0  # All assets are emitted
    assert bb_a_usd.balanceOf(BAURA_BAL) == 0  # All assets are emitted

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
        assert len(tx.events["TreeDistribution"]) == 2  # graviAURA and bBB_A_USD
        assert bb_a_usd.balanceOf(AURABAL_STRAT_NEW) == 0  # All BB_A_USD gets processed

        chain.sleep(13 * 100)
        chain.mine()

        # Withdraw
        user = accounts.at(USER, force=True)
        prev_user_balance = want.balanceOf(USER)
        auraBal_vault.withdrawAll({"from": user})
        assert want.balanceOf(USER) > prev_user_balance

        C.print("[green]Simulation successful![/green]")
    else:
        safe.post_safe_tx()
