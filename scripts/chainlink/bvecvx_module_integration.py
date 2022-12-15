from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

LINK_MANTISSA = 55e18
# sourced from running `brownie test --gas` in https://github.com/petrovska-petro/BveCvxDivestModule_BadgerDAO
GAS_LIMIT = 800_000


def enable_module():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)

    safe = interface.IGnosisSafe_v1_3_0(
        r.badger_wallets.treasury_voter_multisig, owner=voter.account
    )
    module = voter.contract(r.safe_modules.treasury_voter.bvecvx_divest)

    safe.enableModule(r.safe_modules.treasury_voter.bvecvx_divest)
    # allow keeper cl to trigger upkeeps
    module.addExecutor(r.chainlink.keeper_registry)

    voter.post_safe_tx()


def register_bvecvx_module():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)
    techops.init_chainlink()

    techops.chainlink.register_upkeep(
        "BveCvxVoterModule",
        r.safe_modules.treasury_voter.bvecvx_divest,
        GAS_LIMIT,
        LINK_MANTISSA,
    )

    techops.post_safe_tx()
