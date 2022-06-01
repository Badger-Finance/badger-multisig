from helpers.addresses import registry
from great_ape_safe import GreatApeSafe


# will sweep BADGER from dev to techops for future emissions
def main(token="BADGER"):
    safe = GreatApeSafe(registry.arbitrum.badger_wallets.dev_multisig)

    token_contract = safe.contract(registry.arbitrum.treasury_tokens[token])
    safe.take_snapshot([token_contract])

    token_contract.transfer(
        registry.arbitrum.badger_wallets.techops_multisig,
        token_contract.balanceOf(safe),
    )

    safe.print_snapshot()
    safe.post_safe_tx()
