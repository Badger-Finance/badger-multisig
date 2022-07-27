from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# only set to true when actually ready to post and exec on mainnet
COW_PROD = False

# artificially create slippage on the quoted price from cowswap
COEF = 0.9825

# time after which cowswap order expires
DEADLINE = 60 * 60 * 3

# percentage of the bribes that is used to buyback $badger
# ref: https://forum.badger.finance/t/bip-95-graviaura-regulations/5716
BADGER_SHARE = 0.25

SAFE = GreatApeSafe(r.badger_wallets.techops_multisig)
SAFE.init_badger()
SAFE.init_cow(prod=COW_PROD)
PROCESSOR = SAFE.contract(r.aura_bribes_processor)

# tokens involved during processing
WETH = interface.IWETH9(r.treasury_tokens.WETH, owner=SAFE.account)
BADGER = interface.ERC20(r.treasury_tokens.BADGER, owner=SAFE.account)
AURA = interface.ERC20(r.treasury_tokens.AURA, owner=SAFE.account)


def claim_and_sell_for_weth():
    bribes_dest = GreatApeSafe(PROCESSOR.address)
    bribes_dest.take_snapshot(r.bribe_tokens_claimable.values())

    claimed = SAFE.badger.claim_bribes_hidden_hands()

    for addr, mantissa in claimed.items():
        order_payload, order_uid = SAFE.badger.get_order_for_processor(
            sell_token=SAFE.contract(addr),
            mantissa_sell=int(mantissa),
            buy_token=WETH,
            deadline=DEADLINE,
            coef=COEF,
            prod=COW_PROD,
        )
        PROCESSOR.sellBribeForWeth(order_payload, order_uid)

    SAFE.post_safe_tx()


def sell_weth():
    weth_total = WETH.balanceOf(PROCESSOR)
    badger_share = int(WETH.balanceOf(PROCESSOR) * BADGER_SHARE)
    aura_share = int(WETH.balanceOf(PROCESSOR) - badger_share)
    assert badger_share + aura_share == weth_total

    order_payload, order_uid = SAFE.badger.get_order_for_processor(
        sell_token=WETH,
        mantissa_sell=badger_share,
        buy_token=BADGER,
        deadline=DEADLINE,
        coef=COEF,
        prod=COW_PROD,
    )
    PROCESSOR.swapWethForBadger(order_payload, order_uid)

    order_payload, order_uid = SAFE.badger.get_order_for_processor(
        sell_token=WETH,
        mantissa_sell=aura_share,
        buy_token=AURA,
        deadline=DEADLINE,
        coef=COEF,
        prod=COW_PROD,
    )
    PROCESSOR.swapWethForAURA(order_payload, order_uid)

    # since the swapWeth methods each set their own approval, multicalling them
    # will make them replace each other. this performs one more final overwrite
    PROCESSOR.setCustomAllowance(WETH, weth_total)

    SAFE.post_safe_tx()


def emit_tokens():
    if AURA.balanceOf(PROCESSOR) > 0:
        PROCESSOR.swapAURATobveAURAAndEmit()
    if BADGER.balanceOf(PROCESSOR) > 0:
        PROCESSOR.emitBadger()
    SAFE.post_safe_tx(call_trace=True)
