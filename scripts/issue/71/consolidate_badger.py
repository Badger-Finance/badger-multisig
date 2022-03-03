from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface
from rich.console import Console

CONSOLE = Console()

DEV_MULTISIG = registry.eth.badger_wallets.dev_multisig
OLD_OPS_MULTISIG = registry.eth.badger_wallets.ops_multisig_old
TREASURY_VAULT = registry.eth.badger_wallets.treasury_vault_multisig

BADGER_GEYSER = registry.eth.badger_geyser

TOLERANCE = 0.95

def main(upgrade="true", simulation="false"):
    badger_token = interface.IBadger(registry.eth.treasury_tokens.BADGER)

    old_multi = GreatApeSafe(OLD_OPS_MULTISIG)

    old_devProxyAdmin = interface.IProxyAdmin(
        registry.eth.badger_wallets.opsProxyAdmin_old,
        owner=old_multi.account
    )
    dao_treasury = interface.ISimpleTimelockWithVoting(
        registry.eth.badger_wallets.DAO_treasury,
        owner=old_multi.account
    )

    if upgrade == "true":
        ## == Upgrade DAO_Treasury to new logic from the opsMultisig_old == ##

        # Save storage variabls for later
        treasury_balance = badger_token.balanceOf(dao_treasury.address)
        token = dao_treasury.token()
        releaseTime = dao_treasury.releaseTime()
        beneficiary = dao_treasury.beneficiary()
        
        # Upgrades logic and verifies storage
        new_logic = registry.eth.logic.SimpleTimelockWithVoting
        old_devProxyAdmin.upgrade(dao_treasury.address, new_logic)

        assert treasury_balance == badger_token.balanceOf(dao_treasury.address)
        assert token == dao_treasury.token()
        assert releaseTime == dao_treasury.releaseTime()
        assert beneficiary == dao_treasury.beneficiary()
        # Beneficiary is currently the DAO_Agent
        assert dao_treasury.beneficiary() == registry.eth.badger_wallets.fees

        # Nonces are messed up on this multi - replace 76 (on-chain rejection)
        old_multi.post_safe_tx(replace_nonce=76)

    else:
        # Simulates upgrade of contract
        if simulation == "true":
            new_logic = registry.eth.logic.SimpleTimelockWithVoting
            old_devProxyAdmin.upgrade(dao_treasury.address, new_logic)

        safe = GreatApeSafe(DEV_MULTISIG)
        treasury_vault = GreatApeSafe(TREASURY_VAULT)
        safe.take_snapshot(tokens=[registry.eth.treasury_tokens.BADGER])
        treasury_vault.take_snapshot(tokens=[registry.eth.treasury_tokens.BADGER])

        # Contracts needed
        controller = interface.IController(
            registry.eth.controllers.native,
            owner=safe.account
        )
        balance_checker = interface.IBalanceChecker(
            registry.eth.helpers.balance_checker,
            owner=safe.account
        )
        dao_treasury = interface.ISimpleTimelockWithVoting(
            registry.eth.badger_wallets.DAO_treasury,
            owner=safe.account
        )
        bBadger_vault = interface.ISettV4h(
            registry.eth.sett_vaults.bBADGER,
            owner=safe.account
        )
        bBadger_strat = interface.IStrategy(
            registry.eth.strategies["native.badger"],
            owner=safe.account
        )

        ## == Release all BADGER from DAO_Treasury to devMulti == ##
        
        # Sets new beneficiary
        dao_treasury.setBeneficiary(DEV_MULTISIG)
        assert dao_treasury.beneficiary() == DEV_MULTISIG

        treasury_balance = badger_token.balanceOf(dao_treasury.address)
        gov_balance = badger_token.balanceOf(DEV_MULTISIG)

        # Release BADGER to devMultisig
        dao_treasury.release()

        balance_checker.verifyBalance(
            badger_token.address,
            DEV_MULTISIG,
            treasury_balance + gov_balance
        )

        ## == Transfer missing BADGER to Geyser and withdrawAll to vault == ##
        geyser_balance = badger_token.balanceOf(BADGER_GEYSER)
        strategy_balanceOf = bBadger_strat.balanceOf()
        geyser_deficit = strategy_balanceOf - geyser_balance

        # Ensure geyser is in deficit
        assert geyser_deficit > 0
        
        # Transfer missing BADGER to Geyser
        badger_token.transfer(BADGER_GEYSER, geyser_deficit, {"from": safe.address})

        CONSOLE.print(f"{geyser_deficit / 1e18} BADGERs were transfer to the Geyser!\n")

        balance_checker.verifyBalance(
            badger_token.address,
            BADGER_GEYSER,
            geyser_deficit + (geyser_balance * TOLERANCE) # Geyser balance may change from post
        )

        # Once the Geyser has enough BADGER within, we can
        # withdrawAll to transfer all BADGER from strat to the vault
        controller.withdrawAll(bBadger_vault.token())

        assert bBadger_vault.available() >= strategy_balanceOf
        assert bBadger_strat.balanceOf() == 0
        assert badger_token.balanceOf(BADGER_GEYSER) == 0

        # Transfer remaining of amount received from the DAO_treasury to
        # the treaury vault multisig
        amount = treasury_balance - geyser_deficit
        treasury_vault_balance = badger_token.balanceOf(TREASURY_VAULT)
        badger_token.transfer(TREASURY_VAULT, amount, {"from": safe.address})

        balance_checker.verifyBalance(
            badger_token.address,
            TREASURY_VAULT,
            amount + treasury_vault_balance
        )

        safe.print_snapshot()
        treasury_vault.print_snapshot()

        safe.post_safe_tx(post=(simulation != "true"))
