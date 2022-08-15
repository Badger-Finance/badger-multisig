from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

    aurabal = vault.contract(r.treasury_tokens.AURABAL)
    aurabal_rewards = vault.contract(r.aura.aurabal_rewards)

    vault.take_snapshot(tokens=[aurabal])

    aurabal_amount = aurabal.balanceOf(vault)

    aurabal.approve(aurabal_rewards, aurabal_amount)
    aurabal_rewards.stakeAll()

    assert aurabal_rewards.balanceOf(vault) == aurabal_amount

    vault.post_safe_tx(skip_preview=True)
