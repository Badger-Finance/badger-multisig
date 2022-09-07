from brownie import ZERO_ADDRESS

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


COW_PROD = False


def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    bal = vault.contract(r.treasury_tokens.BAL)
    usdc = vault.contract(r.treasury_tokens.USDC)
    aura = vault.contract(r.treasury_tokens.AURA)
    aurabal = vault.contract(r.treasury_tokens.AURABAL)
    wrapper = vault.contract(r.aura.wrapper)
    aurabal_rewards = vault.contract(r.aura.aurabal_rewards)

    vault.take_snapshot([bal, usdc, aura, aurabal])
    vault.init_cow()
    vault.cow.market_sell(
        aura, usdc, aura.balanceOf(vault), deadline=60*60*4, coef=.9825
    )

    bal_to_deposit = bal.balanceOf(vault)
    wrapper_aurabal_out = wrapper.getMinOut(bal_to_deposit, 9950)
    bal.approve(wrapper, bal_to_deposit)
    wrapper.deposit(bal_to_deposit, wrapper_aurabal_out, True, ZERO_ADDRESS)

    # might as well stake all aurabal
    rewards_balance_before = aurabal_rewards.balanceOf(vault)
    aurabal.approve(aurabal_rewards, aurabal.balanceOf(vault))
    aurabal_rewards.stakeAll()
    assert rewards_balance_before < aurabal_rewards.balanceOf(vault)

    vault.post_safe_tx()
