from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface

TREASURY_OPS = registry.eth.badger_wallets.treasury_ops_multisig

def main(peak="badger"):
    safe = GreatApeSafe(registry.ibbtc.dfdBadgerShared)
    safe.init_badger()

    if peak == "badger":
        badger_peak = interface.IPeak(registry.ibbtc.badgerPeak, owner=safe.account)
        badger_peak.approveContractAccess(TREASURY_OPS)
        assert badger_peak.approved(TREASURY_OPS)
    else:
        byvWbtc_peak = interface.IPeak(registry.ibbtc.byvWbtcPeak, owner=safe.account)
        byvWbtc_peak.approveContractAccess(TREASURY_OPS)
        assert byvWbtc_peak.approved(TREASURY_OPS)

    safe.post_safe_tx()
