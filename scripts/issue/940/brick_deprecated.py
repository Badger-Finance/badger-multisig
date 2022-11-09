from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import interface, chain, Contract
from brownie_tokens import MintableForkToken
from rich.console import Console
from eth_abi import encode_abi


console = Console()

NEW_PROXY_ADMIN = "0x0000000000000000000000000000000000000001"


def main(queue="false", sim="true"):
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)
    safe.init_badger()

    registry = safe.contract(r.registry_v2, interface.IBadgerRegistryV2)

    versions = [registry.versions(i) for i in range(3)]
    deprecated = [list(registry.getFilteredProductionVaults(x, 0)) for x in versions]
    # flatten
    deprecated = [safe.contract(x[0]) for sublist in deprecated for x in sublist]

    # confirm deprecated vaults
    console.print(f"Found {len(deprecated)} deprecated vaults:")
    console.print([x.name() for x in deprecated])

    if queue == "true":
        proxy_admin = safe.contract(r.badger_wallets.devProxyAdmin)
        for vault in deprecated:
            console.print(f"Queueing `changeProxyAdmin` for {vault.name()}")
            safe.badger.queue_timelock(
                target_addr=proxy_admin.address,
                signature="changeProxyAdmin(address,address)",
                data=encode_abi(
                    ["address", "address"],
                    [vault.address, NEW_PROXY_ADMIN],
                ),
                dump_dir="data/badger/timelock/changeProxyAdmin/",
                delay_in_days=4,
            )

        safe.post_safe_tx()

    else:
        if sim != "true":
            safe.badger.execute_timelock("data/badger/timelock/changeProxyAdmin/")
            safe.post_safe_tx()
        else:
            proxy_admin = Contract(
                r.badger_wallets.devProxyAdmin, owner=safe.badger.timelock
            )
            for vault in deprecated:
                chain.snapshot()

                console.print(
                    f"changing proxy admin for {vault.address} to {NEW_PROXY_ADMIN}"
                )
                proxy_admin.changeProxyAdmin(vault, NEW_PROXY_ADMIN)

                # arbitrary small amount to ensure funds can be minted
                amount = 1e8
                token = MintableForkToken(vault.token(), owner=safe.account)
                token._mint_for_testing(safe, amount)
                token.approve(vault, amount)

                # edge case: https://etherscan.io/address/0x4b92d19c11435614CD49Af1b589001b7c08cD4D5#writeProxyContract
                if vault.address == "0x4b92d19c11435614CD49Af1b589001b7c08cD4D5":
                    vault.deposit(amount, [])
                else:
                    vault.deposit(amount)

                # not all vaults have `withdrawAll` selector
                vault.withdraw(vault.balanceOf(safe))

                chain.revert()
