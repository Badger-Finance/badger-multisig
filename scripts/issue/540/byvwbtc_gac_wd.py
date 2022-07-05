import json
import os
import web3

from brownie import accounts, chain, Contract, interface, web3
from brownie.test.managers.runner import RevertContextManager as reverts
from eth_abi import encode_abi
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ETH, registry


console = Console()

# Get addresses
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin
DEV_MULTI = registry.eth.badger_wallets.dev_multisig
TREASURY_OPS = registry.eth.badger_wallets.treasury_ops_multisig

GAC = registry.eth.GlobalAccessControl
YEARN_SETT = registry.eth.yearn_vaults.byvWBTC
YEARN_NEW_LOGIC = registry.eth.logic.SimpleWrapperGatedUpgradeable
TIMELOCK = registry.eth.governance_timelock

# Set up safe
safe = GreatApeSafe(DEV_MULTI)
safe.init_badger()

UPGRADE_SIG = "upgrade(address,address)"
TX_DIR = "data/badger/timelock/upgrade_byvwbtc_gac_wd/"
WHALE = "0x6a7ed7a974d4314d2c345bd826daca5501b0aa1e"


def main(queue="true", simulation="false"):
    # UPGRADE block
    if queue == "true":
        safe.badger.queue_timelock(
            target_addr=DEV_PROXY,
            signature=UPGRADE_SIG,
            data=encode_abi(
                ["address", "address"],
                [YEARN_SETT, YEARN_NEW_LOGIC],
            ),
            dump_dir=TX_DIR,
            delay_in_days=4,
        )
    else:
        vault_proxy = interface.ISimpleWrapperGatedUpgradeable(
            YEARN_SETT, owner=DEV_MULTI
        )

        prev_affiliate = vault_proxy.affiliate()
        prev_manager = vault_proxy.manager()
        prev_guardian = vault_proxy.guardian()
        prev_wd_fee = vault_proxy.withdrawalFee()
        prev_wd_threshold = vault_proxy.withdrawalMaxDeviationThreshold()
        prev_experimental_mode = vault_proxy.experimentalMode()
        prev_experimental_vault = vault_proxy.experimentalVault()

        if simulation == "true":
            proxy_admin = interface.IProxyAdmin(
                registry.eth.badger_wallets.devProxyAdmin, owner=TIMELOCK
            )
            proxy_admin.upgrade(YEARN_SETT, YEARN_NEW_LOGIC)
        else:
            safe.badger.execute_timelock(TX_DIR)

        vault_proxy.setTreasury(TREASURY_OPS)

        assert prev_affiliate == vault_proxy.affiliate()
        assert prev_manager == vault_proxy.manager()
        assert prev_guardian == vault_proxy.guardian()
        assert prev_wd_fee == vault_proxy.withdrawalFee()
        assert prev_wd_threshold == vault_proxy.withdrawalMaxDeviationThreshold()
        assert prev_experimental_mode == vault_proxy.experimentalMode()
        assert prev_experimental_vault == vault_proxy.experimentalVault()
        assert TREASURY_OPS == vault_proxy.treasury()
        assert GAC == vault_proxy.GAC()

        if simulation == "true":
            # Transfer funds to user
            user = accounts[3]
            whale = accounts.at(WHALE, force=True)
            whale_balance = int(vault_proxy.balanceOf(WHALE) * 0.8)
            vault_proxy.transfer(user.address, whale_balance, {"from": whale})

            underlying = interface.IERC20(vault_proxy.token())
            affiliate = vault_proxy.affiliate()
            treasury = vault_proxy.treasury()

            # Test wd fee accrued by treasury not governance
            prev_gov_balance = underlying.balanceOf(affiliate)
            prev_treasury_balance = underlying.balanceOf(treasury)

            vault_proxy.withdraw({"from": user})

            assert underlying.balanceOf(treasury) > prev_treasury_balance
            assert underlying.balanceOf(affiliate) == prev_gov_balance

            # Assert pausing works
            gac = interface.IGac(vault_proxy.GAC(), owner=DEV_MULTI)
            gac_guardian = accounts.at(gac.WAR_ROOM_ACL(), force=True)
            gac.pause({"from": gac_guardian})
            with reverts('Pausable: GAC Paused'):
                vault_proxy.withdraw(123, {"from": user})

    if simulation != "true":
        safe.post_safe_tx()
