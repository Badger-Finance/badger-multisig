from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from helpers.utils import approx
from brownie import accounts, interface, chain
from rich.console import Console
from eth_abi import encode_abi

C = Console()

NEW_LOGIC = registry.eth.logic["remBadger"]
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin
USERS_AMOUNTS = {
    "0x138Dd537D56F2F2761a6fC0A2A0AcE67D55480FE": 1788000000000000000000,  # 1788
    "0x39e40AB1eAEc3daBd19c6830f24cF6342Df7f476": 11388000000000000000000,  # 11,387 + 1
}

# For testing purposes, in practice each user will transfer their BADGER amount to the governance multisig
BADGER_WHALE = registry.eth.badger_wallets.treasury_vault_multisig


def queue():
    main(queue="true", simulation="false")


def execute():
    main(queue="false", simulation="false")


def simulation():
    main(queue="false", simulation="true")


def main(queue="true", simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()

    print(registry.eth.sett_vaults.remBADGER)
    rembadger = safe.contract(registry.eth.sett_vaults.remBADGER, interface.IRemBadger)
    badger = safe.badger.badger

    if queue == "true":
        safe.badger.queue_timelock(
            target_addr=DEV_PROXY,
            signature="upgrade(address,address)",
            data=encode_abi(
                ["address", "address"],
                [rembadger.address, NEW_LOGIC],
            ),
            dump_dir="data/badger/timelock/upgrade_remBadger_2_0/",
            delay_in_days=4,
        )
    else:
        ### === Execute upgrade === ###

        assert rembadger.depositsEnded() == True

        # Setting all variables, we'll use them later
        prev_available = rembadger.available()
        prev_gov = rembadger.governance()
        prev_keeper = rembadger.keeper()
        prev_token = rembadger.token()
        prev_controller = rembadger.controller()
        prev_balance = rembadger.balance()
        prev_min = rembadger.min()
        prev_max = rembadger.max()
        prev_getPricePerFullShare = rembadger.getPricePerFullShare()

        # Execute upgrade
        if simulation == "true":
            # Execute upgrade
            timelock = accounts.at(registry.eth.governance_timelock, force=True)
            proxyAdmin = interface.IProxyAdmin(DEV_PROXY, owner=timelock)
            proxyAdmin.upgrade(rembadger.address, NEW_LOGIC)
            # Have user transfer BADGER to governance (whale transfer BADGER for the time being)
            for deposit_user, deposit_amount in USERS_AMOUNTS.items():
                user = accounts.at(BADGER_WHALE, force=True)
                assert badger.balanceOf(user) >= deposit_amount
                badger.transfer(safe.account, deposit_amount, {"from": user})
                assert badger.balanceOf(safe.account) >= deposit_amount
        else:
            safe.badger.execute_timelock("data/badger/timelock/upgrade_remBadger_2_0/")

        ## Checking all variables are as expected
        assert prev_available == rembadger.available()
        assert prev_gov == rembadger.governance()
        assert prev_keeper == rembadger.keeper()
        assert prev_token == rembadger.token()
        assert prev_controller == rembadger.controller()
        assert prev_balance == rembadger.balance()
        assert prev_min == rembadger.min()
        assert prev_max == rembadger.max()
        assert prev_getPricePerFullShare == rembadger.getPricePerFullShare()

        C.print("[green]remBadger upgrade successful[/green]")

        ### === Perform atomic operations === ###

        # Take snapshot
        safe.take_snapshot([badger])

        # Enables deposits through new function
        rembadger.enableDeposits()
        assert rembadger.depositsEnded() == False

        # Governance deposits for the userss
        for deposit_user, deposit_amount in USERS_AMOUNTS.items():
            prev_balance = rembadger.balance()
            prev_getPricePerFullShare = rembadger.getPricePerFullShare()
            assert badger.balanceOf(safe.account) >= deposit_amount
            assert rembadger.balanceOf(deposit_user) == 0

            badger.approve(rembadger, deposit_amount)
            rembadger.depositFor(deposit_user, deposit_amount)
            C.print(f"User balance: {rembadger.balanceOf(deposit_user)/1e18} remBADGER")

            assert prev_balance + deposit_amount == rembadger.balance()
            assert approx(
                prev_getPricePerFullShare, rembadger.getPricePerFullShare(), 0.0001
            )  # There is a 2 wei increase in the second deposit for some reason (perhaps Brownie weirdness?)
            assert approx(
                rembadger.balanceOf(deposit_user),
                (deposit_amount * 1e18) / prev_getPricePerFullShare,
                0.1,
            )

        # Governance bricks deposit to restore final state
        rembadger.brickDeposits()
        assert rembadger.depositsEnded() == True

        ### === Final Simulation === ###
        if simulation == "true":
            for deposit_user, deposit_amount in USERS_AMOUNTS.items():
                chain.snapshot()
                # User withdraws and recovers its original BADGER (no more since emissions ended)
                user = accounts.at(deposit_user, force=True)
                prev_balance = badger.balanceOf(deposit_user)
                rembadger.withdrawAll({"from": user})
                after_balance = badger.balanceOf(deposit_user)
                withdrawn = after_balance - prev_balance
                assert approx(withdrawn, deposit_amount, 0.1)
                C.print(f"User balance withdrawn: {withdrawn/1e18} BADGER")
                chain.revert()

    if simulation == "false":
        safe.post_safe_tx()
