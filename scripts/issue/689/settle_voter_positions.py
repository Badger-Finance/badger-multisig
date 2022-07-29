from pycoingecko import CoinGeckoAPI

from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import Contract, ZERO_ADDRESS


PROD = False

# thresholds
MAX_BAL_DEPOSIT = 12_000 * 1e18
MAX_WBTC_SELL = 1.5

vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
bal = voter.contract(r.treasury_tokens.BAL)


def mint_aurabal_and_lock_aura():
    voter.init_balancer()
    voter.init_aura()

    wrapper = voter.contract(r.aura.wrapper)
    aura = voter.contract(r.treasury_tokens.AURA)
    aurabal = voter.contract(r.treasury_tokens.AURABAL)
    vlaura = vault.contract(r.aura.vlAURA)

    voter.take_snapshot([bal, aura, aurabal])

    # mint auraBAL up to MAX_BAL_DEPOSIT
    to_deposit = bal.balanceOf(voter)
    if to_deposit > MAX_BAL_DEPOSIT:
        to_deposit = MAX_BAL_DEPOSIT

    bal.approve(wrapper,to_deposit)
    wrapper.deposit(
        to_deposit,  # uint256 _amount
        wrapper.getMinOut(to_deposit, 9950),  # uint256 _minOut
        False,  # bool _lock
       ZERO_ADDRESS # address _stakeAddress
    )

    # transfer to vault to eventually deposit into bauraBAL
    aurabal_amount = aurabal.balanceOf(voter)
    aurabal.transfer(vault, aurabal_amount)

    # test before aura fees are claimed for voter
    if not PROD:
        from brownie_tokens import MintableForkToken
        aura = MintableForkToken(r.treasury_tokens.AURA, owner=voter.account)
        aura._mint_for_testing(voter, 500e18)
    
    before = vlaura.balances(voter)[0] / 1e18

    # lock all of voters aura
    aura.approve(voter.aura.aura_locker, aura.balanceOf(voter))
    voter.aura.aura_locker.lock(
        voter.address, 
        aura.balanceOf(voter)
    )

    after = vlaura.balances(voter)[0] / 1e18
    print(f"Received {after - before} vlAURA")
    
    voter.print_snapshot()
    voter.post_safe_tx()


def sell_bal_for_wbtc():
    voter.init_cow(prod=PROD)

    wbtc = voter.contract(r.treasury_tokens.WBTC)

    ids = ["balancer", "wrapped-bitcoin"]
    prices = CoinGeckoAPI().get_price(ids, "usd")
    bal_usd = prices["balancer"]["usd"]
    wbtc_usd = prices["wrapped-bitcoin"]["usd"]

    max_bal_sell = (wbtc_usd / bal_usd) * MAX_WBTC_SELL

    to_sell = bal.balanceOf(voter) / 1e18

    # sell up to MAX_WBTC_SELL
    if to_sell > max_bal_sell:
        to_sell = max_bal_sell
    
    to_sell_mantissa = int(to_sell * 1e18)
    print(f"Selling {to_sell} BAL")

    voter.cow.market_sell(
        bal, wbtc, to_sell_mantissa, deadline=60*60*4, destination=vault.address
    )
    
    voter.post_safe_tx()

