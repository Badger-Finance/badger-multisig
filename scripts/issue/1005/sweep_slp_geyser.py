"""
original contract taken from here: https://github.com/Badger-Finance/badger-system/blob/master/contracts/badger-geyser/StakingRewardsSignalOnly.sol
"""
from brownie import StakingRewardsSignalOnly, accounts, interface
from eth_abi import encode_abi

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def queue():
    main(True, False, False)


def sim():
    main(True, True, True)


def recover():
    main(False, False, True)


def main(queue=False, sim=False, recover=False):
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    badger = safe.contract(r.treasury_tokens.BADGER)
    geyser = StakingRewardsSignalOnly.at(r.slp_geyser, owner=safe.account)
    geyser_proxy_address = r.slp_geyser
    dev_proxy_admin_address = r.badger_wallets.devProxyAdmin

    safe.init_badger()
    trops.take_snapshot([badger])

    geyser_new_logic_address = r.logic.slp_geyser

    if queue:
        # queue up upgrade to timelock
        safe.badger.queue_timelock(
            target_addr=dev_proxy_admin_address,
            signature="upgrade(address,address)",
            data=encode_abi(
                ["address", "address"],
                [geyser_proxy_address, geyser_new_logic_address],
            ),
            dump_dir="data/badger/timelock/upgrade_slp_geyser/",
            delay_in_days=4,
        )

    # execute upgrade
    if sim:
        timelock = accounts.at(safe.badger.timelock, force=True)
        proxyAdmin = interface.IProxyAdmin(dev_proxy_admin_address, owner=timelock)
        proxyAdmin.upgrade(geyser_proxy_address, geyser_new_logic_address)

    # recover badger from geyser and forward from dev msig to trops
    if recover:
        if not sim:
            safe.badger.execute_timelock("data/badger/timelock/upgrade_slp_geyser/")
        geyser.recoverERC20(badger.address, badger.balanceOf(geyser))
        badger.transfer(trops, badger.balanceOf(safe))

    trops.print_snapshot()

    if not sim:
        safe.post_safe_tx()
