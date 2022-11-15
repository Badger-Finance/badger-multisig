from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import interface
from rich.console import Console


console = Console()


def set_new_gov():
    # change gov to 0x21CF9b77F88Adf8F8C98d7E33Fe601DC57bC0893 (governance_timelock) for all v1 deprecated vaults
    dev = GreatApeSafe(r.badger_wallets.dev_multisig)
    dev.init_badger()

    gov_timelock = r.governance_timelock
    registry = dev.contract(r.registry_v2, interface.IBadgerRegistryV2)

    deprecated = list(registry.getFilteredProductionVaults("v1", 0))
    deprecated = [dev.contract(x[0]) for x in deprecated]
    deprecated.remove(r.yearn_vaults.byvWBTC)

    # confirm deprecated vaults
    console.print(f"Found {len(deprecated)} deprecated vaults:")
    console.print([x.name() for x in deprecated])

    for vault in deprecated:
        console.print(f"{vault.name()} gov: {vault.governance()}")
        vault.setGovernance(gov_timelock)
        assert vault.governance() == gov_timelock

    dev.post_safe_tx()


def change_new_proxy_admin(proxy_owner):
    """
    proxy_owner: msig name of proxy admin owner (dev or ops)

    all proxy admins in lists will be changed to 0x20Dce41Acca85E8222D6861Aa6D23B6C941777bF (devProxyAdmin)

    proxy owner:
        - dev_multisig:
            - proxy admin: 0x9215cBDCDe25629d0e3D69ee5562d1b444Cf69F9 (proxyAdminDev)
                - `changeProxyAdmin` - 0x6615e67b8b6b6375d38a0a3f937cd8c1a1e96386 (guardian access control)
                - `changeProxyAdmin` - 0xdDB2dfad74F64F14bb1A1cbaB9C03bc0eed74493 (badger controller)

        - old_ops:
            - proxy admin: 0x4599F2913a3db4E73aA77A304cCC21516dd7270D (opsProxyAdmin_old)
                - `changeProxyAdmin` - 0x660802fc641b154aba66a62137e71f331b6d787a (badgerTree)
                - `changeProxyAdmin` - 0x0a4f4e92c3334821ebb523324d09e321a6b0d8ec (rewardsLogger)
    """

    assert proxy_owner in ("dev", "ops")

    old_proxy_admin = (
        r.badger_wallets.devUngatedProxyAdmin
        if proxy_owner == "dev"
        else r.badger_wallets.opsProxyAdmin_old
    )
    new_proxy_admin = r.badger_wallets.devProxyAdmin

    proxies = {
        "ops": [r.badger_wallets.badgertree, r.rewardsLogger],
        "dev": [r.guardian, r.GatedMiniMeController],
    }

    safe = GreatApeSafe(
        r.badger_wallets.dev_multisig
        if proxy_owner == "dev"
        else r.badger_wallets.ops_multisig_old
    )

    old_proxy_admin = safe.contract(
        r.badger_wallets.devUngatedProxyAdmin
        if proxy_owner == "dev"
        else r.badger_wallets.opsProxyAdmin_old
    )

    for proxy in proxies[proxy_owner]:
        console.print(
            f"p`changing proxy admin for {proxy} from {old_proxy_admin} to {new_proxy_admin}"
        )
        old_proxy_admin.changeProxyAdmin(proxy, new_proxy_admin)

    safe.post_safe_tx(skip_preview=True)
