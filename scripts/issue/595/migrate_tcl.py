from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_balancer()
    vault.init_aura()
    

    bpt = vault.contract(r.balancer.B_20_BTC_80_BADGER)
    # mainly to ensure no dust is left on snap
    vault.take_snapshot(tokens=[bpt.address])

    (_, _, _, rewards) = vault.aura.get_pool_info(bpt)
    rewards = vault.contract(rewards)

    vault.balancer.unstake_all(bpt)

    bpt_amount = bpt.balanceOf(vault)

    bal_before_stake = rewards.balanceOf(vault)
    vault.aura.deposit_and_stake(bpt, bpt_amount)
    assert rewards.balanceOf(vault) > bal_before_stake

    vault.post_safe_tx()
