from brownie import Contract

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)

    bvecvx_pricer = techops.contract(Contract(r.cvx_bribes_processor).pricer())
    gravi_pricer = techops.contract(Contract(r.aura_bribes_processor).pricer())

    for pricer in [bvecvx_pricer, gravi_pricer]:
        if pricer.slippage() != 499:
            pricer.setSlippage(499)

    techops.post_safe_tx(call_trace=True)
