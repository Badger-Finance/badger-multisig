from brownie import Contract

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    safe.init_convex()

    pool2 = Contract(registry.eth.treasury_tokens.badgerWBTC_f, owner=safe.account)
    pool2_bal = pool2.balanceOf(safe)
    safe.take_snapshot([pool2])
    safe.convex.deposit_all_and_stake(pool2)
    _, _, _, rewards = safe.convex.get_pool_info(pool2)

    assert Contract(rewards, owner=safe.account).balanceOf(safe) == pool2_bal

    safe.print_snapshot()
    safe.post_safe_tx(call_trace=True)
