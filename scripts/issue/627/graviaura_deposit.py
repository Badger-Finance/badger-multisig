from great_ape_safe import GreatApeSafe
from helpers.addresses import r

def main():
    safe = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    aura = safe.contract(r.treasury_tokens.AURA)
    graviaura = safe.contract(r.sett_vaults.graviAURA)

    safe.take_snapshot(
        tokens=[aura, graviaura]
    )

    aura.approve(graviaura, aura.balanceOf(safe))
    graviaura.depositAll()

    safe.post_safe_tx()