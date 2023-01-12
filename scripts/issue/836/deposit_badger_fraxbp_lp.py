from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

console = Console()


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_convex()

    lp = vault.contract(r.treasury_tokens.badgerFRAXBP_f_lp)

    (_, _, _, rewards) = vault.convex.get_pool_info(lp)
    rewards = vault.contract(rewards)
    rewards_before = rewards.balanceOf(vault)

    vault.take_snapshot(tokens=[lp.address])

    vault.convex.deposit_all_and_stake(lp)

    rewards_after = rewards.balanceOf(vault)
    delta = rewards_after - rewards_before

    assert delta > 0

    console.print(f"{rewards_before=}")
    console.print(f"{rewards_after=}")
    console.print(f"{delta=}")

    vault.print_snapshot()
    vault.post_safe_tx()
