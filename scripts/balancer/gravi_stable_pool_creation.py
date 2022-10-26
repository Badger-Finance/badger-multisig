import eth_abi

from brownie import accounts, Contract, interface, ZERO_ADDRESS
from decimal import Decimal
from typing import List

from great_ape_safe import GreatApeSafe
from great_ape_safe.ape_api.balancer import Balancer
from great_ape_safe.ape_api.helpers.balancer.weighted_math import WeightedMath
from helpers.addresses import registry


WBTC_AMOUNT = 15
BALANCER_STABLE_FACTORY = "0xf9ac7B9dF2b3454E841110CcE5550bD5AC6f875F"
GRAVIAURA_WHALE = "0x465b357Bbac5F6f3BC78669Db6980f9Eaa21D0C2"

# Params for pool creation
POOL_NAME = "Balancer graviAURA Stable Pool"
SYMBOL = "B-graviAURA-STABLE"
TOKENS = [
    registry.eth.sett_vaults.graviAURA,
    registry.eth.treasury_tokens.AURA,
]
AMPLIFICATION = 1000  # Max is 5000
RATE_PROVIDERS = [
    "0xd5Fd7CEe66c6502F38fA2be0Ad61F6cfB6449CA3",
    "0x0000000000000000000000000000000000000000",
]
TOKEN_RATE_CACHE_DURATION = [1000, 1000]
EXEMPT_FROM_YIELD = [False, False]
SWAP_FEE_PERCENTAGE = 10000000000000000
OWNER = "0xBA1BA1ba1BA1bA1bA1Ba1BA1ba1BA1bA1ba1ba1B"


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    safe.init_balancer()

    factory = interface.IBalancerStablePoolFactory(
        BALANCER_STABLE_FACTORY, owner=safe.account
    )
    pool_address = factory.create(
        POOL_NAME,
        SYMBOL,
        TOKENS,
        AMPLIFICATION,
        RATE_PROVIDERS,
        TOKEN_RATE_CACHE_DURATION,
        EXEMPT_FROM_YIELD,
        SWAP_FEE_PERCENTAGE,
        OWNER,
    ).return_value

    whale = accounts.at(GRAVIAURA_WHALE, force=True)

    graviaura = safe.contract(registry.eth.sett_vaults.graviAURA)

    transfer_balance = int(graviaura.balanceOf(whale) / 2)

    graviaura.transfer(safe.address, transfer_balance, {"from": whale})
    aura = safe.contract(registry.eth.treasury_tokens.AURA)
    bpt = interface.IBalancerStablePool(pool_address, owner=safe.account)

    safe.take_snapshot([graviaura.address, aura.address, bpt.address])

    aura_to_deposit = aura.balanceOf(safe.address)

    graviaura_to_deposit = int(
        aura_to_deposit / graviaura.getPricePerFullShare() * 1e18
    )

    underlyings = [graviaura, aura]
    amounts = [graviaura_to_deposit, aura_to_deposit]
    safe.balancer.deposit_and_stake(
        underlyings, amounts, bpt, stake=False, initial_deposit=True
    )

    safe.print_snapshot()
    safe.post_safe_tx()
