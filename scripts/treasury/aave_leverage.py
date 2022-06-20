"""
  Given Token In and OUT, Leverage functions
"""
import requests
import json
from great_ape_safe import GreatApeSafe
from brownie import Contract
from helpers.addresses import registry

multisigAddress = registry.eth.badger_wallets.dev_multisig

## Signer
safe = GreatApeSafe(multisigAddress)

## Mainnet
AAVE_LENDING_POOL = safe.contract("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9")

WBTC = safe.contract("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

USDC = safe.contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

DEPOSIT_TOKEN = WBTC ## We deposit wBTC and Buy it
BORROW_TOKEN = USDC ## We borrow USDC and use it to buy wBTC

## Returns price in ETH
PRICE_ORACLE = safe.contract("0xA50ba011c48153De246E5192C8f9258A2ba79Ca9")

## UniV2 Router
UNIV2_ROUTER = safe.contract("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")


def main():
  """
    Example function, setup with Deposit Amount and Leverage ratio
  """
  deposit(123)
  lever_up(5_000) ## 50%

def deposit(amount):
  """
    Deposit into AAVE, earns basic interest, LM incentives and allows to lever
  """
  DEPOSIT_TOKEN.approve(AAVE_LENDING_POOL, amount)
  AAVE_LENDING_POOL.deposit(DEPOSIT_TOKEN, amount, safe.address, 0)



def lever_up(percent_bps):
  """
    Given total borrow amounts, we will use `percent_bps` of it to borrow BORROW_TOKEN
  """
  ## Get total borrowable
  info = AAVE_LENDING_POOL.getUserAccountData(safe.address)
  print("info")
  print(info)

  available_borrows_eth = info[2]
  print("available_borrows_eth")
  print(available_borrows_eth)

  ## From ETH to USDC
  usdc_to_eth = PRICE_ORACLE.getAssetPrice(BORROW_TOKEN)

  ## Calculate USDC we can borrow
  usdc_we_can_borrow = ((available_borrows_eth * 10**(BORROW_TOKEN.decimals())) // usdc_to_eth) * percent_bps // 10_000

  print("usdc_we_can_borrow")
  print(usdc_we_can_borrow)

  ## Borrow USDC
  AAVE_LENDING_POOL.borrow(BORROW_TOKEN, usdc_we_can_borrow, 2, 0, safe.address)

  ## Sell USDC for more wBTC
  BORROW_TOKEN.approve(UNIV2_ROUTER, usdc_we_can_borrow)
  swap_result = UNIV2_ROUTER.swapExactTokensForTokens(
        usdc_we_can_borrow,
        0, ## NOTE: We could use oracle here
        [BORROW_TOKEN, DEPOSIT_TOKEN],
        safe,
        9999999999
  )

  ## NOTE: Can be done with onChain Pricer for better prices
  to_reinvest = swap_result.return_value[-1]

  print("to_reinvest")
  print(to_reinvest)

  ## Deposit wBTC into pool
  deposit(to_reinvest)

def repay(amount_to_repay):
  BORROW_TOKEN.approve(AAVE_LENDING_POOL, amount_to_repay)
  AAVE_LENDING_POOL.repay(BORROW_TOKEN, amount_to_repay, 2, safe.address)

def delever(debt_to_repay):
  """
    NOTE: Incomplete
  """
  ## Given amount of debt_to_repay, withdraw what is possible and repay
  info = AAVE_LENDING_POOL.getUserAccountData(safe.address)
  collateral_in_eth = info[0]
  debt_in_eth = info[1]

  usdc_to_eth = PRICE_ORACLE.getAssetPrice(BORROW_TOKEN)

  debt_in_usdc = ((debt_in_eth * 10**6) // usdc_to_eth)

  ## How much wBTC do we need to withdraw, to repay this debt?


  ## Withdraw X

def delever_once():
  """
    Note: Incomplete
  """
  ## Get all the withdrawable, minus a 5% buffer

  ## Withdraw

  ## Swap to USC

  ## Repay

def withdraw(ratio_bps):
  ## TODO:
  ## Require no debt
  ## Withdraw Value in BPS
  """
    Note: Incomplete
  """