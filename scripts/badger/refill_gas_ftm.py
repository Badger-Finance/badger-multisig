from brownie import accounts, Wei

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


EXTRA_WALLETS = []  # also consider these badger wallets that do not prefix ops_

DEFAULT_AMOUNT = 20e18  # target balance for any ops_* badger wallet
EXEC_AMOUNT = 10e18  # target balance for any ops_executor* badger wallet
OVERRIDE_AMOUNT = {  # override DEFAULT_AMOUNT for exceptional badger wallets
    "ops_botsquad": 500e18,
    "ops_deployer": 50e18,
    "ops_external_harvester": 30e18,
}
MIN_TRANSFER = 2e18  # if difference is less than min, transfer min amount instead


def main():
    safe = GreatApeSafe(registry.ftm.badger_wallets.techops_multisig)
    safe.take_snapshot(tokens=[])

    candidates = registry.ftm.badger_wallets.copy()

    total_ftm = 0
    wallets = {}
    for wallet_name, wallet_address in candidates.items():
        # only refill ops_* wallets
        if not (wallet_name.startswith("ops_") or wallet_name in EXTRA_WALLETS):
            continue
        if wallet_name == "techops_multisig":
            # no need to send ourselves eth
            continue

        # figure out desired end balance
        ftm_balance = accounts.at(wallet_address, force=True).balance()
        if wallet_name in OVERRIDE_AMOUNT:
            post_topup_amount = OVERRIDE_AMOUNT[wallet_name]
        elif "ops_executor" in wallet_name:
            post_topup_amount = EXEC_AMOUNT
        else:
            post_topup_amount = DEFAULT_AMOUNT

        # figure out deposit amount and transfer
        if ftm_balance < post_topup_amount:
            # needs top-up
            wallets[wallet_name] = GreatApeSafe(wallet_address)
            wallets[wallet_name].take_snapshot(tokens=[])
            top_up = post_topup_amount - ftm_balance
            if top_up < MIN_TRANSFER:
                top_up = MIN_TRANSFER
            total_ftm += top_up
            safe.account.transfer(wallet_address, top_up)

    for wallet_name, wallet_obj in wallets.items():
        print(wallet_name)
        wallet_obj.print_snapshot()

    print("treasury_ops_multisig")
    safe.print_snapshot()

    safe.post_safe_tx(skip_preview=True)
