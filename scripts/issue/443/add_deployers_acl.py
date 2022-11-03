from brownie import accounts, interface

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

    deployers = [
        wallet for wallet in registry.eth.badger_wallets.keys() if "deployer" in wallet
    ]

    for deployer in deployers:
        address = registry.eth.badger_wallets[deployer]
        for role in roles:
            keeper_acl.grantRole(role, address)

    for deployer in deployers:
        address = registry.eth.badger_wallets[deployer]
        for role in roles:
            assert keeper_acl.hasRole(role, address)

    if simulation == "true":
        deployer = accounts.at(registry.eth.badger_wallets[deployers[0]], force=True)
        keeper_acl.earn(BVECVX_SETT, {"from": deployer})
        keeper_acl.harvest(BVECVX_STRATEGY, {"from": deployer})

    safe.post_safe_tx(call_trace=True)
