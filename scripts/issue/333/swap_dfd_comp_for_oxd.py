from decimal import Decimal

from brownie import interface

from helpers.addresses import registry
from great_ape_safe import GreatApeSafe


VAULT = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
TROPS = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
DFD = interface.ERC20(registry.eth.treasury_tokens.DFD, owner=TROPS.account)
COMP = interface.ERC20(registry.eth.treasury_tokens.COMP, owner=TROPS.account)
USDC = interface.ERC20(registry.eth.treasury_tokens.USDC, owner=TROPS.account)


def move_dfd_to_trops():
    # move dsd to treasury ops
    VAULT.take_snapshot([DFD])
    TROPS.take_snapshot([DFD])

    # since dfd isnt owned by trops yet, overwrite from param
    DFD.transfer(TROPS, DFD.balanceOf(VAULT), {'from': VAULT.account})

    VAULT.print_snapshot()
    TROPS.print_snapshot()


def allow_cowswap_relayer():
    TROPS.init_cow()
    DFD.approve(TROPS.cow.vault_relayer, DFD.balanceOf(TROPS))
    COMP.approve(TROPS.cow.vault_relayer, COMP.balanceOf(TROPS))
    TROPS.post_safe_tx(call_trace=True)


def swap_for_usdc():
    # swap dsd for usdc
    # swap comp for usdc
    TROPS.init_cow()
    TROPS.cow.market_sell(DFD, USDC, DFD.balanceOf(TROPS), coef=.98)
    TROPS.cow.market_sell(COMP, USDC, DFD.balanceOf(TROPS), coef=.98)
    TROPS.post_safe_tx(call_trace=True)


def bridge_usdc_to_ftm(mantissa):
    # bridge said usdc to fantom
    mantissa = Decimal(mantissa)
    TROPS.init_anyswap()
    info = TROPS.anyswap.get_token_bridge_info(
        registry.eth.treasury_tokens.USDC, chain_id_origin=1
    )
    anytoken = info['anyToken']['address']

    router = interface.IAnyswapV6Router(info['router'], owner=TROPS.account)
    USDC.approve(router, mantissa)
    router.anySwapOutUnderlying['address,address,uint256,uint256'](
        anytoken, TROPS, mantissa, 250
    )

    TROPS.post_safe_tx(call_trace=True)


def swap_usdc_for_oxd():
    # swap for oxd
    pass
