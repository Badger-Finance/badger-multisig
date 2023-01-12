"""
ref: https://github.com/smartcontractkit/keeper/blob/master/contracts/UpkeepRegistrationRequests.sol
"""

from brownie import chain, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


LINK_MANTISSA = 50e18
UPKEEP_ID_REMBADGER_22Q3 = 127  # https://keepers.chain.link/mainnet/127
UPKEEP_ID_TREE_22Q3 = 128  # https://keepers.chain.link/mainnet/128

SAFE = GreatApeSafe(r.badger_wallets.techops_multisig)
RELAYER = SAFE.contract(
    r.chainlink.upkeep_registration_requests, interface.IUpkeepRegistrationRequests
)
LINK = SAFE.contract(r.treasury_tokens.LINK, interface.ILinkToken)

SAFE.init_badger()
SAFE.init_chainlink()


def sim():
    cancel_q2(sim=True)
    # need 50 blocks between cancel and link retrieval
    chain.mine(51)
    register_q3(sim=True)


def cancel_q2(sim=False):
    # cancel tree dripper q2
    SAFE.take_snapshot([LINK])
    SAFE.chainlink.keeper_registry.cancelUpkeep(UPKEEP_ID_REMBADGER_22Q3)
    SAFE.chainlink.keeper_registry.cancelUpkeep(UPKEEP_ID_TREE_22Q3)
    if not sim:
        SAFE.post_safe_tx(call_trace=True)


def register_q3(sim=False):
    # retrieve link
    SAFE.chainlink.keeper_registry.withdrawFunds(UPKEEP_ID_REMBADGER_22Q3, SAFE)
    SAFE.chainlink.keeper_registry.withdrawFunds(UPKEEP_ID_TREE_22Q3, SAFE)

    # register upkeeps for new drippers
    SAFE.chainlink.register_upkeep(
        "TreeDripper2022Q4", r.drippers.tree_2022_q4, 300_000, LINK_MANTISSA
    )
    SAFE.chainlink.register_upkeep(
        "RemBadgerDripper2022Q4", r.drippers.rembadger_2022_q4, 300_000, LINK_MANTISSA
    )

    # update watchlist on the gas station
    SAFE.badger.set_gas_station_watchlist()

    if not sim:
        SAFE.post_safe_tx(call_trace=True)
    else:
        SAFE.post_safe_tx(skip_preview=True)
