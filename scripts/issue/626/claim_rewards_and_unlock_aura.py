from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import chain

def main(sim="False"):
    safe = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    aura = safe.contract(r.treasury_tokens.AURA)
    graviaura = safe.contract(r.sett_vaults.graviAURA)

    safe.take_snapshot(tokens=[aura, graviaura])

    safe.init_aura()

    if sim == "True":
        # will revert now, needs simulation on timestamp > 1666828800 for all to expire
        chain.mine(timestamp=1666829800)
    safe.aura.aura_locker.processExpiredLocks(False)

    safe.aura.claim_all(option=2)

    # deposit in graviAURA
    aura.approve(graviaura, aura.balanceOf(safe))
    graviaura.depositAll()

    if sim == "True":
        safe.post_safe_tx(skip_preview=True)
    else:
        safe.post_safe_tx(call_trace=True)
