from decimal import Decimal

from brownie import web3, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


def main(amount=1500):
    mantissa = int(Decimal(amount) * Decimal('1e18'))
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    badger = interface.ERC20(
        registry.eth.treasury_tokens.BADGER, owner=safe.account
    )

    safe.take_snapshot([badger])

    bribe_vault = interface.IBribeVault(
        registry.eth.hidden_hand.bribe_vault, owner=safe.account
    )
    balancer_briber = interface.ITokenmakBribe(
        registry.eth.hidden_hand.balancer_briber, owner=safe.account
    )

    # https://etherscan.io/address/0x7816b3d0935d668bcfc9a4aab5a84ebc7ff320cf#code#L935
    prop = web3.solidityKeccak(['address'], [registry.eth.balancer.B_20_BTC_80_BADGER_GAUGE])

    badger.approve(bribe_vault, mantissa)
    balancer_briber.depositBribeERC20(
        prop, # bytes32 proposal
        badger, # address token
        mantissa, # uint256 amount
    )

    safe.print_snapshot()
    safe.post_safe_tx(call_trace=True)