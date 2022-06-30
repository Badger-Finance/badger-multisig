import json
import os
import web3

from brownie import accounts, chain, Contract, interface, web3
from eth_abi import encode_abi
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ETH, registry


console = Console()

# Get addresses
DEV_PROXY = ADDRESSES_ETH["badger_wallets"]["devProxyAdmin"]
DEV_MULTI = ADDRESSES_ETH["badger_wallets"]["dev_multisig"]
TECH_OPS = ADDRESSES_ETH["badger_wallets"]["techops_multisig"]
GAC = "0x9c58B0D88578cd75154Bdb7C8B013f7157bae35a"
YEARN_SETT = ADDRESSES_ETH["yearn_vaults"]["byvWBTC"]
YEARN_NEW_LOGIC = ADDRESSES_ETH["logic"]["SimpleWrapperGatedUpgradeable"]
TIMELOCK = ADDRESSES_ETH["governance_timelock"]

# Set up safe
safe = GreatApeSafe(DEV_MULTI)
safe.init_badger()

UPGRADE_SIG = "upgrade(address,address)"
TX_DIR = "data/badger/timelock/upgrade_byvwbtc_gac_wd/"


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
            delay_in_days=6,
        )
    else:
        vault_proxy = safe.contract(YEARN_SETT)

        prev_affiliate = vault_proxy.affiliate()
        prev_manager = vault_proxy.manager()
        prev_guardian = vault_proxy.guardian()
        prev_wd_fee = vault_proxy.withdrawalFee
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

        vault_proxy.setTreasury(TECH_OPS)

        assert prev_affiliate == vault_proxy.affiliate()
        assert prev_manager == vault_proxy.manager()
        assert prev_guardian == vault_proxy.guardian()
        assert prev_wd_fee == vault_proxy.withdrawalFee
        assert prev_wd_threshold == vault_proxy.withdrawalMaxDeviationThreshold()
        assert prev_experimental_mode == vault_proxy.experimentalMode()
        assert prev_experimental_vault == vault_proxy.experimentalVault()
        assert TECH_OPS == vault_proxy.treasury()
        assert GAC == vault_proxy.GAC()

    if simulation != "true":
        safe.post_safe_tx()
