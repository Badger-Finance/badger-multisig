from helpers.addresses import r


# https://etherscan.io/address/0x5a92EF27f4baA7C766aee6d751f754EBdEBd9fae#code#L722
MIN_LOCK_TIME = 594000


def main():
    # deposit 250k usdc and equal amount badger
    script = __import__("scripts.issue.825.seed_fraxbp", fromlist=["seed_fraxbp"])
    vault = script.main()

    vault.init_convex()

    badger_fraxbp = vault.contract(r.treasury_tokens.badgerFRAXBP_f_lp)
    wcvx_badger_fraxbp = vault.contract(r.convex.frax.wcvx_badger_fraxbp)

    # 2. deposit in convex staking frax wrapper
    lp_balance = badger_fraxbp.balanceOf(vault)
    badger_fraxbp.approve(wcvx_badger_fraxbp, lp_balance)
    # https://etherscan.io/address/0xb92e3fD365Fc5E038aa304Afe919FeE158359C88#code#L1397
    wcvx_badger_fraxbp.deposit(lp_balance, vault)

    # ratio of staking version should be 1:1
    staking_lp_balance = wcvx_badger_fraxbp.balanceOf(vault)
    assert staking_lp_balance == lp_balance

    # 3. lock in the vault
    vault.convex.stake_lock(
        wcvx_badger_fraxbp,
        staking_lp_balance,
        MIN_LOCK_TIME,
        vault.convex.VAULT_TYPES["badger_fraxbp"],
        # https://etherscan.io/tx/0x74f4492c78385b633fdecb2200efdd99f7377dbf2e0b94468c06682fb78961c1#eventlog (event #214)
        kek_id="FE2A58EC80B5D297700D8FC6B5ED4A0E258DA0CDC27DA72570E7D43FABB2DC4E",
        lock_additional=True,
    )

    vault.print_snapshot()
    vault.post_safe_tx()
