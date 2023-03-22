from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

LINK_MANTISSA = 80e18
GAS_LIMIT = 720_000


def enable_module():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)

    safe = interface.IGnosisSafe_v1_3_0(
        r.badger_wallets.treasury_voter_multisig, owner=voter.account
    )

    safe.enableModule(r.safe_modules.treasury_voter)

    voter.post_safe_tx()


def register_voter_module():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)
    techops.init_chainlink()

    techops.chainlink.register_upkeep(
        "TreasuryVoterModule", r.safe_modules.treasury_voter, GAS_LIMIT, LINK_MANTISSA
    )

    techops.post_safe_tx()
