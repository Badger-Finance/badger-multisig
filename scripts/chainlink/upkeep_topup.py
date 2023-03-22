"""
UpKeep references:

gas station: https://automation.chain.link/mainnet/89
treasury voter: https://automation.chain.link/mainnet/42960818007215227498102337773007812241122867237937589685113781988946396009556
tree dripper: https://automation.chain.link/mainnet/16015974269903908984725510916384725148630916297368865448620388766630414318319
rembadger dripper: https://automation.chain.link/mainnet/98030557125143332209375009711552185081207413079136145061022651896587613727137
"""

from decimal import Decimal

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main(
    upkeep_id=0,
    topup_amount=0,
    upkeep_id_legacy=0,
    topup_amount_legacy=0,
):
    # cast cli args
    upkeep_id = int(upkeep_id)
    topup_amount = Decimal(topup_amount)
    upkeep_id_legacy = int(upkeep_id_legacy)
    topup_amount_legacy = Decimal(topup_amount_legacy)

    techops = GreatApeSafe(r.badger_wallets.techops_multisig)
    link = techops.contract(r.treasury_tokens.LINK)

    techops.take_snapshot([link])

    cl_registry = techops.contract(r.chainlink.keeper_registry)
    cl_registry_legacy = techops.contract(r.chainlink.keeper_registry_v1_1)

    if upkeep_id != 0 and topup_amount > 0:
        mantissa = int(topup_amount * Decimal(1e18))
        link.approve(cl_registry, mantissa)
        cl_registry.addFunds(upkeep_id, mantissa)

    if upkeep_id_legacy != 0 and topup_amount_legacy > 0:
        mantissa = int(topup_amount_legacy * Decimal(1e18))
        link.approve(cl_registry_legacy, mantissa)
        cl_registry_legacy.addFunds(upkeep_id_legacy, mantissa)

    techops.post_safe_tx()
