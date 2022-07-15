from brownie import accounts
from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ETH, registry

DEV_MULTI = registry.eth.badger_wallets.dev_multisig
BVECVX_STRATEGY = ADDRESSES_ETH["strategies"]["native.vestedCVX"]
BVECVX_SETT = ADDRESSES_ETH["sett_vaults"]["bveCVX"]

def main(simulation="false"):
    safe = GreatApeSafe(DEV_MULTI)
    keeper_acl = safe.contract(registry.eth.keeperAccessControl)

    earner_role = keeper_acl.EARNER_ROLE()
    harvester_role = keeper_acl.HARVESTER_ROLE()
    tender_role = keeper_acl.TENDER_ROLE()

    roles = [earner_role, harvester_role, tender_role]

    executor = registry.eth.badger_wallets.ops_executor1

    for role in roles:
        keeper_acl.grantRole(role, executor)
        assert keeper_acl.hasRole(role, executor)

    if simulation == "true":
        executor = accounts.at(executor, force=True)
        keeper_acl.earn(BVECVX_SETT, {"from": executor})
        keeper_acl.harvest(BVECVX_STRATEGY, {"from": executor})

    safe.post_safe_tx(call_trace=True)
