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
COMPOUND_CONTROLLER = safe.contract("0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B")
    
WBTC = safe.contract("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")
cWBTC = safe.contract("0xccF4429DB6322D5C611ee964527D42E5d685DD6a")
cUSDC = safe.contract("0x39AA39c021dfbaE8faC545936693aC917d5E7563")
USDC = safe.contract("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
WETH = safe.contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

DEPOSIT_TOKEN = WBTC ## We deposit wBTC and Buy it
BORROW_TOKEN = USDC ## We borrow USDC and use it to buy wBTC
C_TOKEN = cWBTC
C_TOKEN_BORROW = cUSDC

## Returns price in USD: TWAP guarded chainlink price feed
## The price of the asset in USD as an unsigned integer scaled up by 10 ^ (36 - underlying asset decimals). E.g. WBTC has 8 decimal places, so the return value is scaled up by 1e28.
## https://compound.finance/docs/prices
PRICE_ORACLE = safe.contract("0x65c816077C29b557BEE980ae3cC2dCE80204A0C5")

## UniV2 Router
UNIV2_ROUTER = safe.contract("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D") 
SUSHI_ROUTER = safe.contract("0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F") 

BPS = 10_000

def main():
  """
    Example function, setup with Deposit Amount and Leverage ratio
  """
  enterMarket()
  deposit(123)
  lever_up(5_000) ## 50%
  repay(123 + 123*.5)
  
def enterMarket():
  """
    Enable market in advance for deposit and borrow
  """
  COMPOUND_CONTROLLER.enterMarkets([C_TOKEN.address, C_TOKEN_BORROW.address])

def deposit(amount):
  """
    Deposit into AAVE, earns basic interest, LM incentives and allows to lever
  """
  DEPOSIT_TOKEN.approve(C_TOKEN, 0)
  DEPOSIT_TOKEN.approve(C_TOKEN, amount)
  C_TOKEN.mint(amount)

def lever_up(percent_bps):
  """
    Given total borrow amounts, we will use `percent_bps` of it to borrow BORROW_TOKEN
  """
  ## Get total borrowable
  collateral = C_TOKEN.balanceOfUnderlying(safe.address).return_value
  print("collateral")
  print(collateral)

  borrowed = C_TOKEN_BORROW.borrowBalanceCurrent(safe.address).return_value
  print("already_borrowed")
  print(borrowed)
  
  col_factor = COMPOUND_CONTROLLER.markets(C_TOKEN)[1]
  print("col_factor")
  print(col_factor)

  ## From DEPOSIT_TOKEN to USD
  wbtc_to_usd = PRICE_ORACLE.getUnderlyingPrice(C_TOKEN)
  print("wbtc_to_usd")
  print(wbtc_to_usd)

  ## Calculate USDC we can borrow: Stablecoins like USDC are fixed at $1.
  collateral_to_usdc = collateral * (wbtc_to_usd // 10**(36 - DEPOSIT_TOKEN.decimals())) * 10**(BORROW_TOKEN.decimals()) // 10**(DEPOSIT_TOKEN.decimals())
  col_factor_limited = collateral_to_usdc * col_factor // 10**18
  usdc_we_can_borrow = (col_factor_limited - borrowed) * percent_bps // BPS

  print("usdc_we_can_borrow")
  print(usdc_we_can_borrow)

  ## Borrow USDC
  C_TOKEN_BORROW.borrow(usdc_we_can_borrow)

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
  BORROW_TOKEN.approve(C_TOKEN_BORROW, 0)
  BORROW_TOKEN.approve(C_TOKEN_BORROW, amount_to_repay)
  
  full_debt = C_TOKEN_BORROW.borrowBalanceCurrent(safe.address).return_value
  if full_debt > amount_to_repay: C_TOKEN_BORROW.repayBorrow(amount_to_repay)
  else:  C_TOKEN_BORROW.repayBorrow(2**256 - 1) ## A value of -1 (i.e. 2256 - 1) can be used to repay the full amount.
  
  if full_debt > amount_to_repay: return amount_to_repay
  else: return full_debt
  
def withdraw(amount_to_withdraw, max_deposited): 
  ##  exchangeRateCurrent is scaled by 10^(18 - 8 + Underlying Token Decimals) 
  expected_ctoken = amount_to_withdraw * 10**(18 - 8 + DEPOSIT_TOKEN.decimals()) / C_TOKEN.exchangeRateCurrent().return_value
  C_TOKEN.approve(C_TOKEN, 0)
  C_TOKEN.approve(C_TOKEN, expected_ctoken * 1.2) ## approve a bit more
  
  full_redeem = True
  if max_deposited > amount_to_withdraw: full_redeem = False
  
  if full_redeem: C_TOKEN.redeem(C_TOKEN.balanceOf(safe.address)) ## use cToken to withdrawAll
  else: C_TOKEN.redeemUnderlying(amount_to_withdraw)

def delever(debt_to_repay):
  """
    NOTE: loop until repay in full of debt_to_repay
  """
  wbtc_to_usd = PRICE_ORACLE.getUnderlyingPrice(C_TOKEN)
  max_wbtc_to_withdraw = (debt_to_repay * 10**(DEPOSIT_TOKEN.decimals())) / ((wbtc_to_usd // 10**(36 - DEPOSIT_TOKEN.decimals())) * 10**(BORROW_TOKEN.decimals()))
  
  debt_paid = 0  
  while debt_paid < debt_to_repay:
  
        ## Given amount of debt_to_repay, withdraw what is possible and repay
        collateral = C_TOKEN.balanceOfUnderlying(safe.address).return_value
        borrowed = C_TOKEN_BORROW.borrowBalanceCurrent(safe.address).return_value
        col_factor = COMPOUND_CONTROLLER.markets(C_TOKEN)[1]

        ## How much wBTC do we need to withdraw, to repay this debt?
        collateral_in_usd = collateral * (wbtc_to_usd // 10**(36 - DEPOSIT_TOKEN.decimals())) * 10**(BORROW_TOKEN.decimals()) / 10**(DEPOSIT_TOKEN.decimals())
  
        ## (collateral_in_usd - available_withdraw_usd) * col_factor >= borrowed 
        available_withdraw_usd = collateral_in_usd - (borrowed * BPS / col_factor)
        assert 0 < available_withdraw_usd and available_withdraw_usd <= collateral_in_usd
        available_withdraw_wbtc = (available_withdraw_usd * 10**(DEPOSIT_TOKEN.decimals()) / 10**(BORROW_TOKEN.decimals())) / (wbtc_to_usd // 10**(36 - DEPOSIT_TOKEN.decimals())) 
        
        ## Cap withdrawal to maximum required for debt_to_repay
        if available_withdraw_wbtc > max_wbtc_to_withdraw: 
           available_withdraw_wbtc = max_wbtc_to_withdraw
        
        ## This loop might withdraw a bit more than required for small residues of debt
        ## Add some buffer (5%) for swap slippage/fee etc
        available_withdraw_wbtc = available_withdraw_wbtc * 1.015  

        ## Cap withdrawal to maximum collateral deposited   
        max_deposited = ((collateral_in_usd - borrowed) * 10**(DEPOSIT_TOKEN.decimals()) / 10**(BORROW_TOKEN.decimals())) / (wbtc_to_usd // 10**(36 - DEPOSIT_TOKEN.decimals()))
        if available_withdraw_wbtc > max_deposited: 
           available_withdraw_wbtc = max_deposited
        
        ## Withdraw X: 
        withdraw(available_withdraw_wbtc, max_deposited)
        
        ## Swap to debt
        DEPOSIT_TOKEN.approve(SUSHI_ROUTER, 0)
        DEPOSIT_TOKEN.approve(SUSHI_ROUTER, available_withdraw_wbtc)
        swap_result = SUSHI_ROUTER.swapExactTokensForTokens(available_withdraw_wbtc, 0, [DEPOSIT_TOKEN, WETH, BORROW_TOKEN], safe, 9999999999) ## oracle TODO
        
        ## Repay
        to_repay = BORROW_TOKEN.balanceOf(safe.address)     
        debt_paid = debt_paid + repay(to_repay)
  

def delever_once():
  """
    Note: deleverage to pay all debt 
  """
  ## Get all the withdrawable, minus a 5% buffer
  ## Get deposited - borrowed, convert to wBTC

  ## Withdraw

  ## Swap to USC

  ## Repay
  borrowed = C_TOKEN_BORROW.borrowBalanceCurrent(safe.address).return_value
  delever(borrowed)  
  assert C_TOKEN_BORROW.borrowBalanceCurrent(safe.address).return_value == 0 ## should have no debt at this moment

def withdraw(ratio_bps):
  ## Require no debt
  ## Withdraw Value in BPS
  """
    Note: please ensure no debt before withdraw, otherwise delever first
  """
  assert ratio_bps > 0 and ratio_bps <= BPS
  
  borrowed = C_TOKEN_BORROW.borrowBalanceCurrent(safe.address).return_value
  assert borrowed == 0
  
  collateral = C_TOKEN.balanceOfUnderlying(safe.address).return_value
  amount_to_withdraw = (ratio_bps * collateral) / (BPS)
  withdraw(amount_to_withdraw, collateral)