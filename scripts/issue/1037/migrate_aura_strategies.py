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
NEW_PIDS = {
    "b80BADGER_20WBTC": 18,
    "b40WBTC_40DIGG_20graviAURA": 19
}


def migrate_badger_and_digg():
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)

    for name, address in STAKING_OPTIMIZER_VAULTS.items():
        C.print(f"Migrating {name}...")
        vault = safe.contract(address)
        strat_current = safe.contract(vault.strategy())
        want = safe.contract(vault.token())

        # 1. Harvest current strat
        (bal_rewards, _) = strat_current.balanceOfRewards()
        # Check that rewards are accrued
        bal_earned = bal_rewards[1]
        C.print(f"BAL earned: {bal_earned / 1e18}")

        tx = strat_current.harvest()
        for event in tx.events["Transfer"]:
            if (
                event["from"] == strat_current.baseRewardPool()
                and event["to"] == strat_current.address
            ):
                value = event["value"]
                assert value == bal_earned
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

    safe.post_safe_tx()

