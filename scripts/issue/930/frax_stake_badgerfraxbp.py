from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# https://etherscan.io/address/0x5a92EF27f4baA7C766aee6d751f754EBdEBd9fae#code#L722
MIN_LOCK_TIME = 594000

vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)

badger_fraxbp = vault.contract(r.treasury_tokens.badgerFRAXBP_f_lp)
stkcvx_badger_fraxbp = vault.contract(r.convex.frax.stk_badger_fraxbp)


def create_vault():
    vault.init_convex()
    # https://etherscan.io/tx/0x4895666dd53a4a6bb00611ee27e846653a2927b0a675a56202ca527e827c3e33#eventlog
    vault.convex.create_vault(stkcvx_badger_fraxbp)

    vault.post_safe_tx()


def stake_in_vault():
    vault.init_convex()

    # 1. unstake and claim rewards from vanilla convex
    vault.convex.unstake_all_and_withdraw_all(badger_fraxbp, claim=1)

    # 2. deposit in convex staking frax wrapper
    lp_balance = badger_fraxbp.balanceOf(vault)
    badger_fraxbp.approve(stkcvx_badger_fraxbp, lp_balance)
    # https://etherscan.io/address/0xb92e3fD365Fc5E038aa304Afe919FeE158359C88#code#L1397
    stkcvx_badger_fraxbp.deposit(lp_balance, vault)

    # ratio of staking version should be 1:1
    staking_lp_balance = stkcvx_badger_fraxbp.balanceOf(vault)
    assert staking_lp_balance == lp_balance

    # 3. lock in the vault
    vault.convex.stake_lock(stkcvx_badger_fraxbp, staking_lp_balance, MIN_LOCK_TIME)

    vault.post_safe_tx()
