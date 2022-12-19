from brownie import Wei, interface, chain
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from rich.console import Console
from helpers.constants import AddressZero

C = Console()

# Vaults involved
STAKING_OPTIMIZER_VAULTS = {
    "b80BADGER_20WBTC": registry.eth.sett_vaults.b80BADGER_20WBTC,
    "b40WBTC_40DIGG_20graviAURA": registry.eth.sett_vaults.b40WBTC_40DIGG_20graviAURA,
}
BAURABAL = registry.eth.sett_vaults.bauraBal
BAURABAL_STRAT_NEW = registry.eth.strategies["native.bauraBal"]

# New PIDs
NEW_PIDS = {"b80BADGER_20WBTC": 18, "b40WBTC_40DIGG_20graviAURA": 19}


def migrate_badger_and_digg():
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)

    for name, address in STAKING_OPTIMIZER_VAULTS.items():
        C.print(f"Migrating {name}...")
        vault = safe.contract(address)
        strat_current = safe.contract(vault.strategy())
        want = safe.contract(vault.token())

        # 1. Harvest current strat
        tx = strat_current.harvest()
        for event in tx.events["Transfer"]:
            if (
                event["from"] == strat_current.baseRewardPool()
                and event["to"] == strat_current.address
            ):
                value = event["value"]
                C.log(f"BAL harvested: {value / 1e18}")
        for event in tx.events["Transfer"]:
            if event["from"] == AddressZero and event["to"] == strat_current.address:
                value = event["value"]
                C.log(f"AURA harvested: {value / 1e18}")
                break

        ### 2. Withdraw assets to vault
        balance_of_pool = strat_current.balanceOfPool()
        balanace_of_vault = want.balanceOf(vault.address)
        balance_total = balanace_of_vault + balance_of_pool

        vault.withdrawToVault()
        assert want.balanceOf(vault.address) == balance_total

        ### 3. Migrate strategy
        strat_new = safe.contract(registry.eth.strategies[f"native.{name}"])
        C.print(f"New strategy for {name}: {strat_new.address}")
        # Confirm parameters
        assert strat_new.BOOSTER() != strat_current.BOOSTER()
        assert strat_new.BOOSTER() == registry.eth.aura.booster
        assert strat_new.pid() == NEW_PIDS[name]
        assert strat_new.balanceOfPool() == 0

        # Set new strategy
        vault.setStrategy(strat_new.address)
        assert vault.strategy() == strat_new.address

        ### 4. Earn vault
        vault.earn()
        balance_of_pool = strat_new.balanceOfPool()
        balanace_of_vault = want.balanceOf(vault.address)
        assert balance_total == balance_of_pool + balanace_of_vault

        C.log("[green]Migration successful![/green]\n")

    safe.post_safe_tx(gen_tenderly=False)


def migrate_aurabal():
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    baurabal = safe.contract(BAURABAL, Interface=interface.ITheVault)
    strat_current = safe.contract(
        baurabal.strategy(), Interface=interface.IAuraBalStaker
    )
    strat_new = safe.contract(BAURABAL_STRAT_NEW, Interface=interface.IAuraBalStaker)
    want = safe.contract(baurabal.token(), Interface=interface.IERC20)

    ## 1. Reduce "minBbaUsdHarvest" threshold on old strategy and Harvest
    bbausd_current = safe.contract(strat_current.BB_A_USD(), Interface=interface.IERC20)
    assert bbausd_current.balanceOf(strat_current) > 0
    strat_current.setMinBbaUsdHarvest(0)
    strat_current.harvest()
    assert bbausd_current.balanceOf(strat_current) == 0

    ##. 2. Sweep new bb_a_USD from old strat
    bbausd_new = safe.contract(strat_new.BB_A_USD(), Interface=interface.IERC20)
    new_bbausd_bal_gov = bbausd_new.balanceOf(safe.account)
    new_bbausd_bal = bbausd_new.balanceOf(strat_current)
    baurabal.sweepExtraToken(bbausd_new.address)
    assert bbausd_new.balanceOf(safe) == new_bbausd_bal_gov + new_bbausd_bal

    ## 3. Migrate strategies
    # Check Integrity
    assert strat_new.want() == strat_current.want()
    assert strat_new.vault() == strat_current.vault()
    assert (
        strat_new.withdrawalMaxDeviationThreshold()
        == strat_current.withdrawalMaxDeviationThreshold()
    )
    assert strat_new.autoCompoundRatio() == strat_current.autoCompoundRatio()
    assert (
        strat_new.claimRewardsOnWithdrawAll()
        == strat_current.claimRewardsOnWithdrawAll()
    )
    assert (
        strat_new.balEthBptToAuraBalMinOutBps()
        == strat_current.balEthBptToAuraBalMinOutBps()
    )

    # Check if var exists
    assert strat_new.BB_A_USD() != strat_current.BB_A_USD()
    assert strat_new.minBbaUsdHarvest() == int(1000e18)
    # Check that threshold is lower than current bb_a_usd balance
    assert strat_new.minBbaUsdHarvest() < new_bbausd_bal

    # Checkpoint balance
    balance = baurabal.balance()
    balance_of_pool = strat_current.balanceOfPool()
    vault_balance = want.balanceOf(baurabal)
    assert balance == balance_of_pool + vault_balance

    # Migrate strategy
    baurabal.withdrawToVault()

    assert strat_current.balanceOf() == 0
    baurabal.setStrategy(strat_new)
    assert baurabal.strategy() == strat_new

    baurabal.earn()

    assert strat_new.balanceOf() > 0
    assert baurabal.balance() == balance

    ## 4. Send new bb_a_usd to strat (and harvest?)
    bbausd_new.transfer(strat_new, new_bbausd_bal)
    assert bbausd_new.balanceOf(strat_new) == new_bbausd_bal
    # Won't harvest since other rewards are yet to be accumulated
    # tests show that harvesiting will process new bbausd

    C.log("[green]Migration successful![/green]\n")

    safe.post_safe_tx(gen_tenderly=False)
