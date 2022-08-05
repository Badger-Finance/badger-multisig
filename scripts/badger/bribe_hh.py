from decimal import Decimal

from brownie import web3, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r 


def main(badger_bribe_in_aura=0, badger_bribe_in_balancer=0):
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    badger_bribe_in_aura = int(badger_bribe_in_aura)
    badger_bribe_in_balancer = int(badger_bribe_in_balancer)

    badger = interface.ERC20(
        r.treasury_tokens.BADGER, owner=safe.account
    )

    safe.take_snapshot([badger])

    bribe_vault = interface.IBribeVault(
        r.hidden_hand.bribe_vault, owner=safe.account
    )

    balancer_briber = interface.ITokenmakBribe(
        r.hidden_hand.balancer_briber, owner=safe.account
    )

    aura_briber = interface.IAuraBribe(
        r.hidden_hand.aura_briber, owner=safe.account
    )

    if badger_bribe_in_aura > 0:
        prop = web3.solidityKeccak(["address"], [badger.address])
        mantissa = int(Decimal(badger_bribe_in_aura) * Decimal(10 ** badger.decimals()))
        badger.approve(bribe_vault, mantissa)

        aura_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
        )

    if badger_bribe_in_balancer > 0:
        prop = web3.solidityKeccak(
            ["address"], [r.balancer.B_20_BTC_80_BADGER_GAUGE]
        )

        mantissa = int(Decimal(badger_bribe_in_balancer) * Decimal(10 ** badger.decimals()))
        badger.approve(bribe_vault, mantissa)

        balancer_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
        )


    safe.print_snapshot()
    safe.post_safe_tx(call_trace=True)
