from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import accounts, interface
from rich.console import Console
from brownie.test.managers.runner import RevertContextManager as reverts

C = Console()

NEW_LOGIC = registry.ftm.logic["theVaultWithoutTree"]
VAULT_ADDRESS = registry.ftm.sett_vaults["bwFTM-WETH-wBTC"]
DEV_PROXY = registry.ftm.badger_wallets.devProxyAdmin
## Account with funds stuck due to integration
USER = "0xB943cdb5622E7Bb26D3E462dB68Ee71D8868C940"


def main(simulation="false"):
    safe = GreatApeSafe(registry.ftm.badger_wallets.dev_multisig)

    vault = interface.ITheVaultWithoutTree(VAULT_ADDRESS, owner=safe.account)

    # Record storage variables
    attributes = {}
    for attr in vault.signatures:
        try:
            attributes[attr] = getattr(vault, attr).call()
        except:
            C.print(f"[red]Error storing {attr}[/red]")
            pass

    ## Check current balances
    initial_shares = vault.balanceOf(USER)
    assert initial_shares > 0

    # Execute upgrade
    proxyAdmin = interface.IProxyAdmin(DEV_PROXY, owner=safe.account)
    proxyAdmin.upgrade(vault.address, NEW_LOGIC)

    ## Confirm balances
    assert initial_shares == vault.balanceOf(USER)

    # Confirm storage variables
    for attr in vault.signatures:
        try:
            assert attributes[attr] == getattr(vault, attr).call()
        except:
            pass

    if simulation == "true":
        # Confirm that user can withdraw
        user = accounts.at(USER, force=True)
        want = interface.ERC20(vault.token())

        initial_bal = want.balanceOf(user)
        vault.withdrawAll({"from": user})

        assert want.balanceOf(user) > initial_bal
        assert vault.balanceOf(user) == 0

    safe.post_safe_tx(post=(simulation != "true"))
