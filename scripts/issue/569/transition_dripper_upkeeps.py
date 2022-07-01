'''
ref: https://github.com/smartcontractkit/keeper/blob/master/contracts/UpkeepRegistrationRequests.sol
'''

from brownie import chain, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


LINK_MANTISSA = 75e18
UPKEEP_ID_TREE_22Q2 = 87 # https://keepers.chain.link/mainnet/87

SAFE = GreatApeSafe(r.badger_wallets.techops_multisig)
RELAYER = SAFE.contract(
    r.chainlink.upkeep_registration_requests,
    interface.IUpkeepRegistrationRequests
)
LINK = SAFE.contract(r.treasury_tokens.LINK, interface.ILinkToken)
STATION = SAFE.contract(r.badger_wallets.gas_station)

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
    SAFE.chainlink.keeper_registry.cancelUpkeep(UPKEEP_ID_TREE_22Q2)
    if not sim:
        SAFE.post_safe_tx(call_trace=True)


def register_q3(sim=False):
    # retrieve link
    SAFE.chainlink.keeper_registry.withdrawFunds(UPKEEP_ID_TREE_22Q2, SAFE)

    # register upkeeps for new drippers
    SAFE.chainlink.register_upkeep(
        'TreeDripper2022Q3',
        r.drippers.tree_2022_q3,
        300_000,
        LINK_MANTISSA
    )
    SAFE.chainlink.register_upkeep(
        'RemBadgerDripper2022Q3',
        r.drippers.rembadger_2022_q3,
        300_000,
        LINK_MANTISSA
    )

    # maintenance on the gas station; top up with ether and update watchlist
    SAFE.account.transfer(STATION, SAFE.account.balance())
    SAFE.badger.set_gas_station_watchlist()

    if not sim:
        SAFE.post_safe_tx(call_trace=True)
    else:
        SAFE.post_safe_tx(skip_preview=True)
