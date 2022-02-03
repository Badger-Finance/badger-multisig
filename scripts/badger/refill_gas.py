from brownie import accounts, Wei

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


EXTRA_WALLETS = ['techops_multisig']

DEFAULT_AMOUNT = 2
OVERRIDE_AMOUNT = {
    'ops_botsquad': 15,
    'ops_deployer': 5,
    'ops_external_harvester': 3,
    'techops_multisig': 15
}


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets['ops_multisig'])
    safe.take_snapshot(tokens=[])

    candidates = registry.eth.badger_wallets.copy()
    candidates.pop('ops_multisig_old')

    total_eth = 0
    wallets = {}
    for wallet_name, wallet_address in candidates.items():
        # only refill ops_* wallets
        if not(wallet_name.startswith('ops_') or wallet_name in EXTRA_WALLETS):
            continue
        if wallet_name == 'ops_multisig':
            # no need to send ourselves eth
            continue

        # figure out desired end balance
        eth_balance = accounts.at(wallet_address, force=True).balance()
        if wallet_name in OVERRIDE_AMOUNT:
            post_topup_amount = OVERRIDE_AMOUNT[wallet_name]
        elif 'ops_executor' in wallet_name:
            post_topup_amount = 1
        else:
            post_topup_amount = DEFAULT_AMOUNT

        # figure out deposit amount and transfer
        if eth_balance < Wei(f'{post_topup_amount} ether'):
            # needs top-up
            wallets[wallet_name] = GreatApeSafe(wallet_address)
            wallets[wallet_name].take_snapshot(tokens=[])
            top_up = Wei(f'{post_topup_amount} ether') - eth_balance
            if top_up < Wei('0.2 ether'):
                top_up = Wei('0.2 ether')
            total_eth += Wei(top_up).to('ether')
            safe.account.transfer(wallet_address, top_up)

    for wallet_name, wallet_obj in wallets.items():
        print(wallet_name)
        wallet_obj.print_snapshot()

    print('ops_multisig')
    safe.print_snapshot()

    safe.post_safe_tx()
