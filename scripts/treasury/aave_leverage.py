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
aWBTC = safe.contract("0x9ff58f4fFB29fA2266Ab25e75e2A8b3503311656")
USDC = safe.contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
WETH = safe.contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

DEPOSIT_TOKEN = WBTC ## We deposit wBTC and Buy it
BORROW_TOKEN = USDC ## We borrow USDC and use it to buy wBTC
A_TOKEN = aWBTC

## Returns price in ETH
PRICE_ORACLE = safe.contract("0xA50ba011c48153De246E5192C8f9258A2ba79Ca9")

## UniV2 Router
UNIV2_ROUTER = safe.contract("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D") 
SUSHI_ROUTER = safe.contract("0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F") 

BPS = 10_000

def main():
  """
    Example function, setup with Deposit Amount and Leverage ratio
  """
  deposit(123)
  lever_up(5_000) ## 50%
  repay(123 + 123*.5)

def deposit(amount):
  """
    Deposit into AAVE, earns basic interest, LM incentives and allows to lever
  """
  DEPOSIT_TOKEN.approve(AAVE_LENDING_POOL, 0)
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
  usdc_we_can_borrow = ((available_borrows_eth * 10**(BORROW_TOKEN.decimals())) // usdc_to_eth) * percent_bps // BPS

  print("usdc_we_can_borrow")
  print(usdc_we_can_borrow)

  ## Borrow USDC
  AAVE_LENDING_POOL.borrow(BORROW_TOKEN, usdc_we_can_borrow, 2, 0, safe.address)

  ## Sell USDC for more wBTC
  BORROW_TOKEN.approve(SUSHI_ROUTER, 0)
  BORROW_TOKEN.approve(SUSHI_ROUTER, usdc_we_can_borrow)
  swap_result = SUSHI_ROUTER.swapExactTokensForTokens(
        usdc_we_can_borrow,
        0, ## NOTE: We could use oracle here
        [BORROW_TOKEN, WETH, DEPOSIT_TOKEN],
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
  BORROW_TOKEN.approve(AAVE_LENDING_POOL, 0)
  BORROW_TOKEN.approve(AAVE_LENDING_POOL, amount_to_repay)
  AAVE_LENDING_POOL.repay(BORROW_TOKEN, amount_to_repay, 2, safe.address)
  
def withdraw(amount_to_withdraw):  
  A_TOKEN.approve(AAVE_LENDING_POOL, 0)
  A_TOKEN.approve(AAVE_LENDING_POOL, amount_to_withdraw)
  AAVE_LENDING_POOL.withdraw(DEPOSIT_TOKEN, amount_to_withdraw, safe.address)

def delever(debt_to_repay):
  """
    NOTE: loop until repay in full of debt_to_repay
  """
  usdc_to_eth = PRICE_ORACLE.getAssetPrice(BORROW_TOKEN)
  wbtc_to_eth = PRICE_ORACLE.getAssetPrice(DEPOSIT_TOKEN)
  max_wbtc_to_withdraw = (debt_to_repay * usdc_to_eth * 10**(DEPOSIT_TOKEN.decimals())) / (wbtc_to_eth * 10**(BORROW_TOKEN.decimals()))
  
  debt_paid = 0  
  while debt_paid < debt_to_repay:
  
        ## Given amount of debt_to_repay, withdraw what is possible and repay
        info = AAVE_LENDING_POOL.getUserAccountData(safe.address)
        collateral_in_eth = info[0]
        debt_in_eth = info[1]
        available_borrows_eth = info[2]
        liq_threshold = info[3]

        ## How much wBTC do we need to withdraw, to repay this debt?
  
        ## (collateral_in_eth - available_withdraw_eth) * liq_threshold >= debt_in_eth 
        ## && collateral_in_eth * liq_threshold >= (debt_in_eth + available_borrows_eth)
        available_withdraw_eth = available_borrows_eth * BPS / liq_threshold 
        assert 0 < available_withdraw_eth and available_withdraw_eth <= collateral_in_eth
        available_withdraw_wbtc = available_withdraw_eth * 10**(DEPOSIT_TOKEN.decimals()) / wbtc_to_eth
        
        ## Cap withdrawal to maximum required for debt_to_repay
        if available_withdraw_wbtc > max_wbtc_to_withdraw: 
           available_withdraw_wbtc = max_wbtc_to_withdraw
        
        ## This loop might withdraw a bit more than required for small residues of debt
        ## Add some buffer (5%) for swap slippage/fee etc
        available_withdraw_wbtc = available_withdraw_wbtc * 1.05  

        ## Cap withdrawal to maximum collateral deposited   
        max_deposited = (collateral_in_eth - debt_in_eth) * 10**(DEPOSIT_TOKEN.decimals()) / wbtc_to_eth
        if available_withdraw_wbtc > max_deposited: 
           available_withdraw_wbtc = max_deposited
        
        ## Withdraw X: 
        withdraw(available_withdraw_wbtc)
        
        ## Swap to debt
        DEPOSIT_TOKEN.approve(SUSHI_ROUTER, 0)
        DEPOSIT_TOKEN.approve(SUSHI_ROUTER, available_withdraw_wbtc)
        swap_result = SUSHI_ROUTER.swapExactTokensForTokens(available_withdraw_wbtc, 0, [DEPOSIT_TOKEN, WETH, BORROW_TOKEN], safe, 9999999999) ## oracle TODO
        
        ## Repay
        to_repay = swap_result.return_value[-1]        
        repay(to_repay)
        debt_paid = debt_paid + to_repay
  

def delever_once():
  """
    Note: deleverage to pay all debt 
  """
  ## Get all the withdrawable, minus a 5% buffer
  ## Get deposited_eth - borrowed_eth, convert to wBTC

  ## Withdraw

  ## Swap to USC

  ## Repay
  info = AAVE_LENDING_POOL.getUserAccountData(safe.address)
  collateral_in_eth = info[0]
  debt_in_eth = info[1]
  
  usdc_to_eth = PRICE_ORACLE.getAssetPrice(BORROW_TOKEN)
  debt_in_usdc = ((debt_in_eth * 10**(BORROW_TOKEN.decimals())) / usdc_to_eth)
  delever(debt_in_usdc)
  
  info = AAVE_LENDING_POOL.getUserAccountData(safe.address)
  assert info[1] == 0 ## should have no debt at this moment

def withdraw(ratio_bps):
  ## Require no debt
  ## Withdraw Value in BPS
  """
    Note: please ensure no debt before withdraw, otherwise delever first
  """
  assert ratio_bps > 0 and ratio_bps <= BPS
  info = AAVE_LENDING_POOL.getUserAccountData(safe.address)
  collateral_in_eth = info[0]
  
  debt_in_eth = info[1]
  assert debt_in_eth == 0
  
  wbtc_to_eth = PRICE_ORACLE.getAssetPrice(DEPOSIT_TOKEN)
  amount_to_withdraw = (ratio_bps * collateral_in_eth * 10**(DEPOSIT_TOKEN.decimals())) / (wbtc_to_eth * BPS)
  withdraw(amount_to_withdraw)