from brownie import Contract, accounts, chain, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


DEV = GreatApeSafe(r.badger_wallets.dev_multisig)
GOV = GreatApeSafe(r.badger_wallets.dev_multisig_deprecated)
OLD_OPS = GreatApeSafe(r.badger_wallets.ops_multisig)
DEPLOYER = GreatApeSafe(r.badger_wallets.ops_deployer)  # for snapshotting

DEADLINE = chain.time() + 60 * 60 * 4


def sim():
    transfer_gov_to_new_msig(True)
    disable_wd_fees(True)
    mock_eoa()
    sweep_fees(True)


def transfer_gov_to_new_msig(sim=False):
    """
    step 1 (issue#260)

    set governance on all bsc setts and strategies to the new dev msig
    """
    for addr in list(r.sett_vaults.values()) + list(r.strategies.values()):
        OLD_OPS.contract(addr).setGovernance(DEV)

    old_interface = interface.IGnosisSafe_v1_2_0_Bsc(OLD_OPS.address)
    print("owners:", old_interface.getOwners())
    print("threshold:", old_interface.getThreshold())

    if not sim:
        OLD_OPS.post_safe_tx_manually()


def disable_wd_fees(sim=False):
    """
    step 2 (issue#58)

    set wd fees on all strat to 0.
    this also prevents collecting more fees on the old addresses
    """
    GOV.take_snapshot(list(r.treasury_tokens.values()) + list(r.sett_vaults.values()))
    DEPLOYER.take_snapshot(
        list(r.treasury_tokens.values()) + list(r.sett_vaults.values())
    )

    for addr in r.strategies.values():
        strat = DEV.contract(addr)
        strat.setWithdrawalFee(0)
        strat.setGovernance(r.badger_wallets.dev_multisig)

    GOV.print_snapshot()
    DEPLOYER.print_snapshot()

    if not sim:
        # need to skip_preview to prevent: BadFunctionCallOutput: Could not decode contract function call to VERSION with return data: b'', output_types: ['string']
        DEV.post_safe_tx(skip_preview=True)


def mock_eoa():
    """
    step 3 (issue#59)

    deployer should send all collected lp fees to GOV

    NOTE: this is for simulation purposes only
    """
    deployer = accounts.at(r.badger_wallets.ops_deployer, force=True)
    for addr in r.lp_tokens.values():
        lp = Contract(addr, owner=deployer)
        lp.transfer(DEV, lp.balanceOf(deployer))


def sweep_fees(sim=False):
    """
    step 4 (issue#60)

    withdraws all collected lp fees into underlying to new dev msig
    """
    GOV.take_snapshot(list(r.treasury_tokens.values()) + list(r.sett_vaults.values()))
    DEV.take_snapshot(list(r.treasury_tokens.values()) + list(r.sett_vaults.values()))

    ROUTER_V1 = GOV.contract(r.pancakeswap.router_v1)
    ROUTER_V2 = GOV.contract(r.pancakeswap.router_v2)

    for addr in r.lp_tokens.values():
        lp = GOV.contract(addr)
        router = ROUTER_V1 if lp.factory() == r.pancakeswap.factory_v1 else ROUTER_V2
        balance = lp.balanceOf(GOV)
        lp.approve(router, balance)
        router.removeLiquidity(lp.token0(), lp.token1(), balance, 0, 0, DEV, DEADLINE)

    GOV.print_snapshot()
    DEV.print_snapshot()

    if not sim:
        GOV.post_safe_tx_manually()
