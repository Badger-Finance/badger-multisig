from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_balancer()
    vault.init_aura()

    reth = vault.contract(r.treasury_tokens.RETH)
    badger = vault.contract(r.treasury_tokens.BADGER)
    bal = vault.contract(r.treasury_tokens.BAL)
    aura = vault.contract(r.treasury_tokens.AURA)
    bpt_badgerreth_old = vault.contract(r.balancer._deprecated.B_50_BADGER_50_RETH)
    bpt_badgerreth_new = vault.contract(r.balancer.B_50_BADGER_50_RETH)

    vault.take_snapshot(
        [reth, badger, aura, bal, bpt_badgerreth_old, bpt_badgerreth_new]
    )

    vault.aura.unstake_all_and_withdraw_all(bpt_badgerreth_old)

    reth_before, badger_before = reth.balanceOf(vault), badger.balanceOf(vault)

    vault.balancer.unstake_all_and_withdraw_all(pool=bpt_badgerreth_old, unstake=False)
    vault.print_snapshot()

    reth_to_deposit, badger_to_deposit = (
        reth.balanceOf(vault) - reth_before,
        badger.balanceOf(vault) - badger_before,
    )

    vault.balancer.deposit_and_stake(
        [badger, reth],
        [badger_to_deposit, reth_to_deposit],
        pool=bpt_badgerreth_new,
        stake=False,
        pool_type="Weighted",
    )

    rewards_contract = vault.contract(vault.aura.get_pool_info(bpt_badgerreth_new)[3])
    bpt_bal = bpt_badgerreth_new.balanceOf(vault)
    vault.aura.deposit_all_and_stake(bpt_badgerreth_new)
    assert rewards_contract.balanceOf(vault) == bpt_bal

    vault.post_safe_tx()
