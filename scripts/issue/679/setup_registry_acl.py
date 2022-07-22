from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import accounts, interface

SAFE = GreatApeSafe(r.badger_wallets.techops_multisig)
DUMMY_VAULT = "0x1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a"

def main(simulation="false"):
    registry = SAFE.contract(r.registry_v2, Interface=interface.IBadgerRegistryV2)
    registry_acl = SAFE.contract(r.registryAccessControl)

    # 1. Grant "DEVELOPER_ROLE" to all deployers
    # NOTE: All deployers will now have permission to index vaults through the ACL,
    # promote up to experimental and demote to any level directly.
    deployers = [
        wallet for wallet in r.badger_wallets.keys() if "deployer" in wallet
    ]
    role = registry_acl.DEVELOPER_ROLE()

    for deployer in deployers:
        address = r.badger_wallets[deployer]
        registry_acl.grantRole(role, address)

    # 2. Set registryAcessControl as the "developer" on the RegistryV2
    registry.setDeveloper(registry_acl.address)
    assert registry.developer() == registry_acl.address

    # 3. Set registryAccessControl key on registry
    registry.set("registryAccessControl", registry_acl.address)
    assert registry.get("registryAccessControl") == registry_acl.address

    if simulation == "true":
        deployer = accounts.at(address, force=True)

        # Test add
        registry_acl.add(DUMMY_VAULT, "v1.5", "name=BTC-CVX,protocol=Badger,behavior=DCA", {"from": deployer})
        assert registry.getVaults("v1.5", registry_acl) == [[DUMMY_VAULT, "v1.5", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"]]

        # Test promote
        registry_acl.promote(DUMMY_VAULT, "v1.5", "name=BTC-CVX,protocol=Badger,behavior=DCA", 3, {"from": deployer})
        assert [DUMMY_VAULT, "v1.5", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"] not in registry.getFilteredProductionVaults("v1.5", 3)
        assert [DUMMY_VAULT, "v1.5", "1", "name=BTC-CVX,protocol=Badger,behavior=DCA"] in registry.getFilteredProductionVaults("v1.5", 1)
    else:
        SAFE.post_safe_tx(call_trace=True)