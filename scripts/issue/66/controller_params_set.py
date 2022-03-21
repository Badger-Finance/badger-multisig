from rich.console import Console
from brownie import interface, accounts, Contract
from helpers.addresses import registry

C = Console()

# addresses involved
NEW_SET_PARAM = registry.arbitrum.badger_wallets.dev_multisig

ACCOUNT_TO_LOAD = ""

# Set new dev_msig as strategist, governance & rewards
def main(broadcast="true"):
    dev = accounts.load(ACCOUNT_TO_LOAD)
    
    print(NEW_SET_PARAM)

    safe = interface.IMultisigWalletWithDailyLimit(
        registry.arbitrum.badger_wallets.dev_multisig_deprecated
    )

    controller = Contract(registry.arbitrum.controller)

    encode_input_set_strategist = controller.setStrategist.encode_input(NEW_SET_PARAM)
    encode_input_set_governance = controller.setGovernance.encode_input(NEW_SET_PARAM)
    encode_input_set_rewards = controller.setRewards.encode_input(NEW_SET_PARAM)

    print(f"encode_input_set_strategist={encode_input_set_strategist}\n")
    print(f"encode_input_set_governance={encode_input_set_governance}\n")
    print(f"encode_input_set_rewards={encode_input_set_rewards}\n")

    if broadcast == "true":
        safe.submitTransaction(
            controller.address, 0, encode_input_set_strategist, {"from": dev}
        )
        safe.submitTransaction(
            controller.address, 0, encode_input_set_governance, {"from": dev}
        )
        safe.submitTransaction(
            controller.address, 0, encode_input_set_rewards, {"from": dev}
        )
