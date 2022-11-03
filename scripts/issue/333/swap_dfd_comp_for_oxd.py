from decimal import Decimal

from brownie import interface, network

from helpers.addresses import registry
from great_ape_safe import GreatApeSafe


if network.chain.id == 1:
    VAULT = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)
    TROPS = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    DFD = interface.ERC20(registry.eth.treasury_tokens.DFD, owner=TROPS.account)
    COMP = interface.ERC20(registry.eth.treasury_tokens.COMP, owner=TROPS.account)
    USDC_ETH = interface.ERC20(registry.eth.treasury_tokens.USDC, owner=TROPS.account)

else:
    TROPS_FTM = GreatApeSafe(registry.ftm.badger_wallets.treasury_ops_multisig)
    USDC_FTM = interface.ERC20(
        registry.ftm.treasury_tokens.USDC, owner=TROPS_FTM.account
    )
    OXD = interface.ERC20(registry.ftm.treasury_tokens.OXD, owner=TROPS_FTM.account)
    WFTM = interface.ERC20(registry.ftm.treasury_tokens.WFTM, owner=TROPS_FTM.account)


def move_dfd_to_trops():
    # move dsd to treasury ops
    VAULT.take_snapshot([DFD])
    TROPS.take_snapshot([DFD])

    # since dfd isnt owned by trops yet, overwrite from param
    DFD.transfer(TROPS, DFD.balanceOf(VAULT), {"from": VAULT.account})

    VAULT.print_snapshot()
    TROPS.print_snapshot()

    VAULT.post_safe_tx(call_trace=True)


def allow_cowswap_relayer():
    TROPS.init_cow()
    DFD.approve(TROPS.cow.vault_relayer, DFD.balanceOf(TROPS))
    COMP.approve(TROPS.cow.vault_relayer, COMP.balanceOf(TROPS))
    TROPS.post_safe_tx(call_trace=True)


def swap_for_usdc():
    # swap dsd for usdc
    # swap comp for usdc
    TROPS.init_cow()
    TROPS.cow.market_sell(DFD, USDC_ETH, DFD.balanceOf(TROPS), coef=0.985)
    TROPS.cow.market_sell(COMP, USDC_ETH, COMP.balanceOf(TROPS), coef=0.985)
    TROPS.post_safe_tx(call_trace=True)


def bridge_usdc_to_ftm(mantissa):
    # bridge said usdc to fantom
    mantissa = Decimal(mantissa)
    TROPS.init_anyswap()
    info = TROPS.anyswap.get_token_bridge_info(
        registry.eth.treasury_tokens.USDC, chain_id_origin=1
    )
    anytoken = info["anyToken"]["address"]

    router = interface.IAnyswapV6Router(info["router"], owner=TROPS.account)
    USDC_ETH.approve(router, mantissa)
    router.anySwapOutUnderlying["address,address,uint256,uint256"](
        anytoken, TROPS_FTM.address, mantissa, 250
    )

    TROPS.post_safe_tx(call_trace=True)


def swap_usdc_for_oxd(amount_mantissa=None):
    # swap for oxd
    TROPS_FTM.init_solidly()
    TROPS_FTM.init_spookyswap()
    TROPS_FTM.take_snapshot([USDC_FTM, OXD])

    TROPS_FTM.spookyswap.swap_tokens_for_tokens(
        USDC_FTM,
        USDC_FTM.balanceOf(TROPS_FTM) if amount_mantissa is None else amount_mantissa,
        [USDC_FTM, WFTM],
    )

    TROPS_FTM.solidly.swap_tokens_for_tokens(
        WFTM, WFTM.balanceOf(TROPS_FTM) * 0.98, [WFTM, OXD]
    )

    TROPS_FTM.print_snapshot()
    TROPS_FTM.post_safe_tx()
