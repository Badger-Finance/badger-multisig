from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main():
    vault = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    vault.init_uni_v3()
    vault.init_convex()

    tokens = [
        vault.contract(registry.eth.treasury_tokens.WBTC),
        vault.contract(registry.eth.treasury_tokens.BADGER),
        vault.contract(registry.eth.treasury_tokens.CRV),
        vault.contract(registry.eth.treasury_tokens.CVX),
        vault.contract(registry.eth.bribe_tokens_claimable.ANGLE)
    ]

    trops.take_snapshot(tokens=tokens)
    vault.take_snapshot(tokens=tokens)

    balances_before = {token: token.balanceOf(vault) for token in tokens}

    vault.uni_v3.collect_fees()
    vault.convex.claim_all()

    for token, balance_before in balances_before.items():
        balance_delta = token.balanceOf(vault) - balance_before
        token.transfer(trops, balance_delta)

    trops.print_snapshot()
    # see dust
    vault.print_snapshot()

    # look at emitted events from reward contract to see exact amounts that are claimed
    vault.post_safe_tx(events=True)
