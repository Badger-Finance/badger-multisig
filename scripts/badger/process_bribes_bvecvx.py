import json

import pandas as pd
from brownie import interface, accounts

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from pycoingecko import CoinGeckoAPI


# only set to true when actually ready to post and exec on mainnet
COW_PROD = False

# artificially create slippage on the quoted price from cowswap
COEF = 0.96

# time after which cowswap order expires
DEADLINE = 60 * 60 * 3

SAFE = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
SAFE.init_badger()
SAFE.init_cow(prod=COW_PROD)
PROCESSOR = SAFE.badger.cvx_bribes_processor

WETH = interface.IWETH9(registry.eth.treasury_tokens.WETH, owner=SAFE.account)
BADGER = interface.ERC20(registry.eth.treasury_tokens.BADGER, owner=SAFE.account)
CVX = interface.ERC20(registry.eth.treasury_tokens.CVX, owner=SAFE.account)

# percentage of the bribes that is used to buyback $badger
BADGER_SHARE = 0.275
CVX_SHARE = 1 - BADGER_SHARE

# percentage of the bribes that are dedicated to the treasury
OPS_FEE = 0.05

# Simulation variables
WETH_WHALE = "0xF04a5cC80B1E94C69B48f5ee68a08CD2F09A7c3E"
BADGER_WHALE = "0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e"
CVX_WHALE = "0xCF50b810E57Ac33B91dCF525C6ddd9881B139332"

# get list of tokens currently active on votium market
with open("data/Votium/merkle/activeTokens.json") as fp:
    ACTIVE_TOKENS = pd.DataFrame(json.load(fp))["value"].tolist()
    # add cvxFXS, not to claim as a bribe, but to sweep it
    ACTIVE_TOKENS.append(registry.eth.treasury_tokens.cvxFXS)
    # luna wormhole token doesnt adhere to erc20
    ACTIVE_TOKENS.remove("0xbd31ea8212119f94a611fa969881cba3ea06fa3d")


def step0_1(sim=False):
    bribes_dest = GreatApeSafe(PROCESSOR.address)
    bribes_dest.take_snapshot(ACTIVE_TOKENS)

    if sim:
        from brownie_tokens import MintableForkToken

        alcx = MintableForkToken(registry.eth.treasury_tokens.ALCX)
        alcx._mint_for_testing(SAFE.badger.strat_bvecvx, 500e18)
        claimed = {alcx.address: 500e18}
    else:
        claimed = SAFE.badger.claim_bribes_votium()
        for token_addr in ACTIVE_TOKENS:
            # handle any non $cvx token present in the strat contract as bribes
            # ref: https://github.com/Badger-Finance/badger-strategies/issues/56
            if token_addr.lower() != CVX.address.lower():
                token_amount = SAFE.badger.sweep_reward_token(token_addr)
                if token_amount > 0:
                    claimed[token_addr] = (
                        claimed.setdefault(token_addr, 0) + token_amount
                    )

    for addr, mantissa in claimed.items():
        order_payload, order_uid = SAFE.badger.get_order_for_processor(
            PROCESSOR,
            sell_token=SAFE.contract(addr),
            mantissa_sell=mantissa,
            buy_token=WETH,
            deadline=DEADLINE,
            coef=COEF,
            prod=COW_PROD,
        )
        PROCESSOR.sellBribeForWeth(order_payload, order_uid)
    SAFE.badger.claim_bribes_convex(ACTIVE_TOKENS)

    bribes_dest.print_snapshot()

    SAFE.post_safe_tx()


def step0(sim=False):
    """can be skipped if step0_1 was successful"""

    bribes_dest = GreatApeSafe(PROCESSOR.address)
    bribes_dest.take_snapshot(ACTIVE_TOKENS)

    if sim:
        from brownie_tokens import MintableForkToken

        alcx = MintableForkToken(registry.eth.treasury_tokens.ALCX)
        alcx._mint_for_testing(SAFE.badger.strat_bvecvx, 500e18)
    else:
        SAFE.badger.sweep_reward_token(registry.eth.treaury_tokens.cvxFXS)
        SAFE.badger.claim_bribes_votium()
        SAFE.badger.claim_bribes_convex(ACTIVE_TOKENS)

    bribes_dest.print_snapshot()

    SAFE.post_safe_tx(call_trace=True)


def step1():
    """can be skipped if step0_1 was successful"""

    want_to_sell = ACTIVE_TOKENS
    want_to_sell.remove("0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b")  # CVX
    want_to_sell.remove("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")  # WETH
    for addr in want_to_sell:
        token = SAFE.contract(addr)
        balance = token.balanceOf(SAFE.badger.cvx_bribes_processor)
        if balance == 0:
            continue
        order_payload, order_uid = SAFE.badger.get_order_for_processor(
            PROCESSOR,
            sell_token=token,
            mantissa_sell=balance,
            buy_token=WETH,
            deadline=DEADLINE,
            coef=COEF,
            prod=COW_PROD,
        )
        PROCESSOR.sellBribeForWeth(order_payload, order_uid)
    SAFE.post_safe_tx(call_trace=True)


def step2(sim=False):
    if sim:
        weth_whale = accounts.at(WETH_WHALE, force=True)
        badger_whale = accounts.at(BADGER_WHALE, force=True)
        cvx_whale = accounts.at(CVX_WHALE, force=True)

        # Modify amounts to transfer to test different cases
        WETH.transfer(PROCESSOR, 9e18, {"from": weth_whale})
        BADGER.transfer(PROCESSOR, 0e18, {"from": badger_whale})
        CVX.transfer(PROCESSOR, 10000e18, {"from": cvx_whale})

    weth_total = WETH.balanceOf(PROCESSOR)
    cvx_total = CVX.balanceOf(PROCESSOR)
    badger_total = BADGER.balanceOf(PROCESSOR)

    ## Estimate the amount of BADGER and CVX to buy
    # Grab prices from coingecko
    ids = ["weth", "convex-finance", "badger-dao"]
    prices = CoinGeckoAPI().get_price(ids, "usd")

    # Estimate total USD value of bribes
    weth_usd_balance = weth_total / 1e18 * prices["weth"]["usd"]
    badger_usd_balance = badger_total / 1e18 * prices["badger-dao"]["usd"]
    cvx_usd_balance = cvx_total / 1e18 * prices["convex-finance"]["usd"]
    total_bribes_usd_balance = weth_usd_balance + badger_usd_balance + cvx_usd_balance

    # Estimate current percentage of BADGER and CVX
    badger_percentage = badger_usd_balance / total_bribes_usd_balance
    cvx_percentage = cvx_usd_balance / total_bribes_usd_balance

    # Estimate BADGER and CVX shares to swap for (NOTE: cvx_split is 1 - badger_split)
    # If processor contains more BADGER than 27.5% of total bribes, don't get any more
    if badger_percentage >= BADGER_SHARE:
        badger_split = 0
    # If processor contains more CVX than 72.5% of total bribes, don't get any more
    elif cvx_percentage >= CVX_SHARE:
        badger_split = 1
    # Obtain BADGER split considering the current amount sitting on the Processor
    else:
        badger_split = (
            BADGER_SHARE * total_bribes_usd_balance - badger_usd_balance
        ) / weth_usd_balance

    badger_share = int(weth_total * badger_split)
    cvx_share = int(weth_total - badger_share)
    assert badger_share + cvx_share == weth_total

    if sim:
        print(f"BADGER split: {badger_split}")
        print(f"CVX split: {1 - badger_split}\n")
        print(f"WETH total: {weth_total}")
        print(f"WETH to sell for Badger: {badger_share}")
        print(f"WETH to sell for CVX: {cvx_share}\n")

    if badger_share > 0:
        order_payload, order_uid = SAFE.badger.get_order_for_processor(
            PROCESSOR,
            sell_token=WETH,
            mantissa_sell=badger_share,
            buy_token=BADGER,
            deadline=DEADLINE,
            coef=COEF,
            prod=COW_PROD,
        )
        PROCESSOR.swapWethForBadger(order_payload, order_uid)

    if cvx_share > 0:
        order_payload, order_uid = SAFE.badger.get_order_for_processor(
            PROCESSOR,
            sell_token=WETH,
            mantissa_sell=cvx_share,
            buy_token=CVX,
            deadline=DEADLINE,
            coef=COEF,
            prod=COW_PROD,
        )
        PROCESSOR.swapWethForCVX(order_payload, order_uid)

    # since the swapWeth methods each set their own approval, multicalling them
    # will make them replace each other. this performs one more final overwrite
    PROCESSOR.setCustomAllowance(WETH, weth_total)

    SAFE.post_safe_tx()


def step3():
    if CVX.balanceOf(PROCESSOR) > 0:
        PROCESSOR.swapCVXTobveCVXAndEmit()
    if BADGER.balanceOf(PROCESSOR) > 0:
        PROCESSOR.emitBadger()
    SAFE.post_safe_tx(call_trace=True)


def step3_a():
    """can be skipped if step3 was successful"""

    if CVX.balanceOf(PROCESSOR) > 0:
        PROCESSOR.swapCVXTobveCVXAndEmit()
    SAFE.post_safe_tx(call_trace=True)


def step3_b():
    """can be skipped if step3 was successful"""

    if BADGER.balanceOf(PROCESSOR) > 0:
        PROCESSOR.emitBadger()
    SAFE.post_safe_tx(call_trace=True)
