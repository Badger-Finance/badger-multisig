from decimal import Decimal

from brownie import accounts, web3, interface, chain
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import ADDRESSES_ETH
from helpers.addresses import registry

console = Console()

DEV_MULTI = registry.eth.badger_wallets.dev_multisig
TECH_OPS = registry.eth.badger_wallets.techops_multisig
TREASURY = registry.eth.badger_wallets.treasury_vault_multisig

HARVEST_FORWARDER = registry.eth.harvest_forwarder

PBTC_STRATEGY_DEP = ADDRESSES_ETH["strategies"]["_deprecated"]["native.pbtcCrv"]["v1"]
PBTC_STRATEGY = ADDRESSES_ETH["strategies"]["native.pbtcCrv"]

OBTC_STRATEGY_DEP = ADDRESSES_ETH["strategies"]["_deprecated"]["native.obtcCrv"]["v1"]
OBTC_STRATEGY = ADDRESSES_ETH["strategies"]["native.obtcCrv"]

OBTC_VAULT = ADDRESSES_ETH["sett_vaults"]["bcrvOBTC"]
PBTC_VAULT = ADDRESSES_ETH["sett_vaults"]["bcrvPBTC"]

PNT = registry.eth.treasury_tokens.PNT
BOR = registry.eth.treasury_tokens.BOR
BORING = registry.eth.treasury_tokens.BORING
BADGER = registry.eth.treasury_tokens.BADGER

STRATEGIES = [PBTC_STRATEGY_DEP, PBTC_STRATEGY, OBTC_STRATEGY_DEP, OBTC_STRATEGY]
STRATEGY_MAPPING = {
    PBTC_STRATEGY_DEP: "pbtcCrv_deprecated",
    PBTC_STRATEGY: "pbtcCrv",
    OBTC_STRATEGY_DEP: "obtcCrv_deprecated",
    OBTC_STRATEGY: "obtcCrv",
}

TOKENS = [PNT, BOR, BORING]
TOKEN_MAPPING = {
    PNT: "PNT",
    BOR: "BOR",
    BORING: "BORING",
}

FEE = 0.2  # 20% to DAO


def sweep_to_techops():
    safe = GreatApeSafe(DEV_MULTI)
    safe.take_snapshot(TOKENS)

    for strategy in STRATEGIES:
        console.print(f"[green]Sweeping {STRATEGY_MAPPING[strategy]}[/green]")
        sweep_strategy(strategy, safe)

    bor_contract = interface.ERC20(BOR, owner=safe.account)
    boring_contract = interface.ERC20(BORING, owner=safe.account)
    pnt_contract = interface.ERC20(PNT, owner=safe.account)

    final_bor_bal = bor_contract.balanceOf(safe.address)
    final_boring_bal = boring_contract.balanceOf(safe.address)
    final_pnt_bal = pnt_contract.balanceOf(safe.address)

    bor_contract.transfer(TECH_OPS, final_bor_bal)
    boring_contract.transfer(TECH_OPS, final_boring_bal)
    pnt_contract.transfer(TECH_OPS, final_pnt_bal)

    assert 0 == bor_contract.balanceOf(DEV_MULTI)
    assert 0 == boring_contract.balanceOf(DEV_MULTI)
    assert 0 == pnt_contract.balanceOf(DEV_MULTI)

    assert final_bor_bal == bor_contract.balanceOf(TECH_OPS)
    assert final_boring_bal == boring_contract.balanceOf(TECH_OPS)
    assert final_pnt_bal == pnt_contract.balanceOf(TECH_OPS)

    console.print(f"BOR swept: {final_bor_bal / 10 ** 18}")
    console.print(f"BORING swept: {final_boring_bal / 10 ** 18}")
    console.print(f"PNT swept: {final_pnt_bal / 10 ** 18}")

    safe.post_safe_tx(call_trace=True)


def sell_for_badger():
    safe = GreatApeSafe(TECH_OPS)
    safe.init_cow(True)

    sell_all_of_token(BOR, safe)
    sell_all_of_token(BORING, safe)
    sell_all_of_token(PNT, safe)

    safe.post_safe_tx(call_trace=True)


def distribute_to_users(obtc_badger_amt: str, pbtc_badger_amt: str):
    obtc_amount_minus_fee = int(int(obtc_badger_amt) * (1 - FEE))
    pbtc_amount_minus_fee = int(int(pbtc_badger_amt) * (1 - FEE))
    obtc_leftover = int(obtc_badger_amt) - obtc_amount_minus_fee
    pbtc_leftover = int(pbtc_badger_amt) - pbtc_amount_minus_fee

    safe = GreatApeSafe(TECH_OPS)
    badger = interface.ERC20(BADGER, owner=safe.account)
    forwarder = interface.IHarvestForwarder(HARVEST_FORWARDER, owner=safe.account)

    badger.approve(HARVEST_FORWARDER, obtc_amount_minus_fee + pbtc_amount_minus_fee)

    forwarder.distribute(BADGER, obtc_amount_minus_fee, OBTC_VAULT)
    forwarder.distribute(BADGER, pbtc_amount_minus_fee, PBTC_VAULT)

    badger.transfer(TREASURY, obtc_leftover + pbtc_leftover)

    safe.post_safe_tx(call_trace=True)


def sweep_strategy(
    strategy_address: str,
    safe: GreatApeSafe,
):
    strategy = interface.IStrategy(strategy_address, owner=safe.account)

    controller_address = strategy.controller()
    controller = interface.IController(controller_address, owner=safe.account)

    for token_address in TOKENS:
        token = interface.ERC20(token_address)

        strategy_balance = token.balanceOf(strategy_address)
        controller_balance = token.balanceOf(controller_address)
        safe_balance_prev = token.balanceOf(safe.address)

        assert 0 == controller_balance

        if strategy_balance > 0:
            readable_amount = strategy_balance / 10 ** token.decimals()
            console.print(
                f"[green]Sweeping {readable_amount} {TOKEN_MAPPING[token_address]} from strategy[/green]"
            )
            controller.inCaseStrategyTokenGetStuck(strategy_address, token_address)
            controller_balance += token.balanceOf(controller_address)
            controller.inCaseTokensGetStuck(token_address, controller_balance)
            assert strategy_balance == token.balanceOf(safe.address) - safe_balance_prev
            assert token.balanceOf(safe.address) > safe_balance_prev

        assert 0 == token.balanceOf(strategy_address)
        assert 0 == token.balanceOf(controller_address)


def sell_all_of_token(token_address: str, safe: GreatApeSafe):
    token = safe.contract(token_address)
    badger = safe.contract(BADGER)

    balance = token.balanceOf(safe.address)
    deadline = 60 * 60 * 24 * 3  # 3 days

    safe.cow.market_sell(token, badger, balance, deadline)
