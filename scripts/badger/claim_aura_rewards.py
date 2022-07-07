from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main(
    msig_name="treasury_voter_multisig",
    redirect_rewards=False,
    destination="0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b",  # defaults to voter_msig
):
    safe = GreatApeSafe(r.badger_wallets[msig_name])
    bal = safe.contract(r.treasury_tokens.BAL)
    aura = safe.contract(r.treasury_tokens.AURA)

    init_balance_bal = bal.balanceOf(safe)
    init_balance_aura = aura.balanceOf(safe)

    safe.init_aura()
    safe.take_snapshot(
        tokens=[bal, aura, r.treasury_tokens.AURABAL, r.sett_vaults.graviAURA]
    )

    if safe.address == r.badger_wallets.treasury_voter_multisig:
        safe.aura.claim_all(option=2)
    else:
        safe.aura.claim_all()

    # sends only delta
    if redirect_rewards == "True":
        if bal.balanceOf(safe) > 0:
            bal.transfer(
                destination,
                bal.balanceOf(safe) - init_balance_bal,
            )
        if aura.balanceOf(safe) > 0:
            aura.transfer(
                destination,
                aura.balanceOf(safe) - init_balance_aura,
            )

    safe.post_safe_tx()
