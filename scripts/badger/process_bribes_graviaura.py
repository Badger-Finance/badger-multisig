from brownie import interface, web3
from pycoingecko import CoinGeckoAPI
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
AURA_SHARE = 1 - BADGER_SHARE

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

    # do not introduce orders if we claim badger or aura bribes
    # likely these assets will be present in the rounds for processing
    # NOTE: badger is directly emitted by the strat to tree
    # NOTE: aura is sent to processor, but should not be sold for weth
    for addr, mantissa in claimed.items():
        addr = web3.toChecksumAddress(addr)
        if addr != BADGER.address and addr != AURA.address:
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
    badger_total = BADGER.balanceOf(PROCESSOR)
    aura_total = AURA.balanceOf(PROCESSOR)

    ## Estimate the amount of BADGER and AURA to buy
    # Grab prices from coingecko
    ids = ["weth", "aura-finance", "badger-dao"]
    prices = CoinGeckoAPI().get_price(ids, "usd")

    # Estimate total USD value of bribes
    weth_usd_balance = weth_total / 1e18 * prices["weth"]["usd"]
    badger_usd_balance = badger_total / 1e18 * prices["badger-dao"]["usd"]
    aura_usd_balance = aura_total / 1e18 * prices["aura-finance"]["usd"]
    total_bribes_usd_balance = weth_usd_balance + badger_usd_balance + aura_usd_balance

    # Estimate current percentage of BADGER and AURA
    badger_percentage = badger_usd_balance / total_bribes_usd_balance
    aura_percentage = aura_usd_balance / total_bribes_usd_balance

    # Estiamte BADGER and AURA shares to swap for (NOTE: aura_split is 1 - badger_split)
    # If processor contains more BADGER than 25% of total bribes, don't get any more
    if badger_percentage >= BADGER_SHARE:
        badger_split = 0
    # If processor contains more AURA than 75% of total bribes, don't get any more
    elif aura_percentage >= AURA_SHARE:
        badger_split = 1
    # Obtain BADGER split considering the current amount sitting on the Processor
    else:
        badger_split = (BADGER_SHARE * total_bribes_usd_balance - badger_usd_balance) / weth_usd_balance

    badger_share = int(weth_total * badger_split)
    aura_share = int(weth_total - badger_share)
    assert badger_share + aura_share == weth_total

    if badger_share > 0:
        order_payload, order_uid = SAFE.badger.get_order_for_processor(
            sell_token=WETH,
            mantissa_sell=badger_share,
            buy_token=BADGER,
            deadline=DEADLINE,
            coef=COEF,
            prod=COW_PROD,
        )
        PROCESSOR.swapWethForBadger(order_payload, order_uid)

    if aura_share > 0:
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
