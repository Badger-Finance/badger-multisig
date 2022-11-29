from brownie import accounts, chain, interface
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ETH


console = Console()

# Get addresses
TECH_OPS = ADDRESSES_ETH["badger_wallets"]["techops_multisig"]
GRAVIAURA_STRATEGY = ADDRESSES_ETH["strategies"]["native.graviAURA"]

# Set up safe
safe = GreatApeSafe(TECH_OPS)
safe.init_badger()

# Other constants
PREV_MIN_OUT_BPS = 9500
MIN_OUT_BPS = 9000
ONE_DAY = 86400


def main(simulation="false"):

    strategy = interface.IVestedAura(GRAVIAURA_STRATEGY, owner=safe.account)

    prev_min_bps = strategy.auraBalToBalEthBptMinOutBps()

    strategy.setAuraBalToBalEthBptMinOutBps(MIN_OUT_BPS)

    after_min_bps = strategy.auraBalToBalEthBptMinOutBps()

    assert after_min_bps == MIN_OUT_BPS
    assert prev_min_bps == PREV_MIN_OUT_BPS
    assert after_min_bps < prev_min_bps

    if simulation:
        harvester = accounts.at(strategy.keeper(), force=True)
        # sleep one day to accrue more rewards
        chain.sleep(ONE_DAY)
        chain.mine()

        # harvest
        strategy.harvest({"from": harvester})

    # Executing all upgrades together
    safe.post_safe_tx()
