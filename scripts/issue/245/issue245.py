from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import interface
from rich.console import Console


console = Console()

NEW_IMPLEMENTATION = "0x67Db14E73C2Dce786B5bbBfa4D010dEab4BBFCF9"


def main():
    """
    upgrade fbveCVX to latest implementation
    """

    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_rari()

    fbveCVX = interface.IFToken(registry.eth.rari['fbveCVX-22'])

    console.print('Current fbveCVX implementation:', fbveCVX.implementation())
    safe.rari.upgrade_ftoken(fbveCVX, NEW_IMPLEMENTATION)
    console.print('New fbveCVX implementation:', fbveCVX.implementation())

    safe.post_safe_tx()
