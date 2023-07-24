from brownie import web3
from decimal import Decimal
from great_ape_safe import GreatApeSafe
from helpers.addresses import r

SAFE = GreatApeSafe(r.badger_wallets.techops_multisig)
SAFE.init_badger()
PROCESSOR = SAFE.contract(r.aura_bribes_processor, from_explorer=True)

USDC = SAFE.contract(r.treasury_tokens.USDC)
LOAN_AMOUNT = 4607936029


def main():
    dev = GreatApeSafe(r.badger_wallets.dev_multisig)
    dev.take_snapshot(r.bribe_tokens_claimable_graviaura.values())
    initial_balance = USDC.balanceOf(dev)

    claimed = SAFE.badger.claim_bribes_hidden_hands(
        claim_from_strat=False, claim_for_strat=True
    )
    # If more than one reward, this should fail
    for token, value in claimed.items():
        assert web3.toChecksumAddress(token) == USDC
        assert Decimal(value) == LOAN_AMOUNT

    # Sweep the total balance of each one of the claimed rewards into the processor
    SAFE.badger.strat_graviaura.sweepRewardToken(USDC)

    # Rage Quit USDC to Dev
    PROCESSOR.ragequit(USDC, True)
    assert USDC.balanceOf(dev) - initial_balance == LOAN_AMOUNT

    dev.print_snapshot()
    SAFE.post_safe_tx()


def transfer_USDC_to_trops():
    dev = GreatApeSafe(r.badger_wallets.dev_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    trops.take_snapshot([USDC])
    initial_balance = USDC.balanceOf(trops)

    USDC.transfer(trops.accunt, LOAN_AMOUNT, {"from": dev.account})

    assert USDC.balanceOf(trops) - initial_balance == LOAN_AMOUNT

    trops.print_snapshot()
    dev.post_safe_tx()
