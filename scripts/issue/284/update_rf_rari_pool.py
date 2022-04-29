from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

TARGET_RF = 0
TARGET_MARKETS = [
    "fUSDC-22",
    "fFEI-22",
    "fDAI-22",
    "fFRAX-22",
    "fDOLA-22",
    "fWBTC-22",
    "fETH-22",
]


def main():
    dev_msig = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)

    dev_msig.init_rari()

    for key, value in registry.eth.rari.items():
        if key in TARGET_MARKETS:
            # check rf
            current_rf = dev_msig.rari.ftoken_get_rf(value)
            if current_rf != TARGET_RF:
                print(f"Current RF for {key} is {current_rf}, updating it to {TARGET_RF}\n")
                # update rf
                dev_msig.rari.ftoken_set_rf(value, TARGET_RF)
            else:
                print(f"Current RF for {key} is the targetted value\n")

    dev_msig.post_safe_tx()
