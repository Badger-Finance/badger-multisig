from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console
from brownie import interface

C = Console()

VAULTS_PIDS = {
    "b80BADGER_20WBTC": 33,
    "b40WBTC_40DIGG_20graviAURA": 34,
}

def main():
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)
    booster = safe.contract(r.aura.booster)

    for vault_id, pid in VAULTS_PIDS.items():
        vault = safe.contract(r.sett_vaults[vault_id])
        strat = interface.IStrategyAuraStaking(vault.strategy(), owner=safe.account)
        want = safe.contract(vault.token())

        C.print(f"[cyan]Migrating gauge for {vault.name()}[/cyan]")

        #### 1. Harvest strategy ####
        strat.harvest()

        #### 2. Withdraw all to vault ####
        vault_balance_before = want.balanceOf(vault.address)
        pool_balance_before = strat.balanceOfPool()
        strat_balance_before = strat.balanceOfWant()
        total_balance_before = vault.balance()
        assert total_balance_before == vault_balance_before + pool_balance_before + strat_balance_before

        # Call withdrawToVault
        vault.withdrawToVault()

        # Confrm balances
        assert want.balanceOf(vault.address) == total_balance_before
        assert strat.balanceOfPool() == 0

        #### 3. set new PID ####
        pid_before = strat.pid()
        baseRewardPool_before = strat.baseRewardPool()

        # Confirm new PIDs info
        old_info = booster.poolInfo(pid_before)
        new_info = booster.poolInfo(pid)
        baseRewardPool_new = new_info["crvRewards"]
        gauge_new = new_info["gauge"]
        assert old_info["lptoken"] == want.address
        assert old_info["lptoken"] == new_info["lptoken"]
        assert baseRewardPool_before != baseRewardPool_new

        # Set new PID
        strat.setPid(pid)

        assert strat.pid() == pid
        assert strat.baseRewardPool() == baseRewardPool_new

        #### 4. Earn ####
        # Ensure that we are not the first ones to deposit on the new gauge
        new_deposit_token = safe.contract(new_info["token"])
        rewards_d_tkn_balance_before = new_deposit_token.balanceOf(baseRewardPool_new)
        assert rewards_d_tkn_balance_before > 0

        gauge_balance_before = want.balanceOf(gauge_new)
        available = vault.available()

        vault.earn()

        # Check that assets move properly
        gauge_balance_after= want.balanceOf(gauge_new)
        rewards_d_tkn_balance_after = new_deposit_token.balanceOf(baseRewardPool_new)
        assert available == gauge_balance_after - gauge_balance_before
        assert available == strat.balanceOfPool()
        assert available == rewards_d_tkn_balance_after - rewards_d_tkn_balance_before
        # Assert that the total amount of tokens remained the same
        assert total_balance_before == vault.balance()

        C.print(f"[green]Migration successful![/green]")

    safe.post_safe_tx()




        
