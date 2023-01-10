"""
ref: https://github.com/smartcontractkit/keeper/blob/master/contracts/UpkeepRegistrationRequests.sol
"""

from brownie import chain, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


LINK_MANTISSA = 80e18
UPKEEP_ID_REMBADGER_22Q4 = 142  # https://keepers.chain.link/mainnet/142
UPKEEP_ID_BVECVX_MODULE = 14270489937535892760600590423564455802049459622872924518248134412357549386527 # https://automation.chain.link/mainnet/14270489937535892760600590423564455802049459622872924518248134412357549386527
SAFE = GreatApeSafe(r.badger_wallets.techops_multisig)
LINK = SAFE.contract(r.treasury_tokens.LINK, interface.ILinkToken)

SAFE.init_badger()
SAFE.init_chainlink()


def sim():
    cancel_q4(sim=True)
    # need 50 blocks between cancel and link retrieval
    chain.mine(51)
    register_2023(sim=True)


def cancel_q4(sim=False):
    # cancel tree dripper q4
    SAFE.take_snapshot([LINK])
    SAFE.chainlink.keeper_registry_v1_1.cancelUpkeep(UPKEEP_ID_REMBADGER_22Q4)
    SAFE.chainlink.keeper_registry.cancelUpkeep(UPKEEP_ID_BVECVX_MODULE)
    if not sim:
        SAFE.post_safe_tx(call_trace=True)


def register_2023(sim=False):
    # retrieve link
    SAFE.chainlink.keeper_registry_v1_1.withdrawFunds(UPKEEP_ID_REMBADGER_22Q4, SAFE)
    SAFE.chainlink.keeper_registry.withdrawFunds(UPKEEP_ID_BVECVX_MODULE, SAFE)

    # register upkeeps for new drippers
    SAFE.chainlink.register_upkeep(
        "TreeDripper2023", r.drippers.tree_2023, 300_000, LINK_MANTISSA
    )
    SAFE.chainlink.register_upkeep(
        "RemBadgerDripper2023", r.drippers.rembadger_2023, 300_000, LINK_MANTISSA
    )

    # update watchlist on the gas station
    SAFE.badger.set_gas_station_watchlist()

    if not sim:
        SAFE.post_safe_tx(call_trace=True)
    else:
        SAFE.post_safe_tx(skip_preview=True)
