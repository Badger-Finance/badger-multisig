from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def enable_module():
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

    # contracts
    module = trops.contract(r.safe_modules.treasury_ops_multisig.fee_collector)
    safe = interface.IGnosisSafe_v1_3_0(
        r.badger_wallets.treasury_ops_multisig, owner=trops.account
    )

    # add `feeToken` balancer/aura vaults
    aura_vaults = [
        trops.contract(r.sett_vaults.b40WBTC_40DIGG_20graviAURA),
        trops.contract(r.sett_vaults.b80BADGER_20WBTC),
    ]
    for vault in aura_vaults:
        token = trops.contract(vault.token())
        pool_id = token.getPoolId()
        # https://etherscan.io/address/0x24a6108D1985B44130f68550C9c43d556720CF17#code#F1#L121
        module.addFeeTokenBalancer(vault, True, pool_id)

    # add `feeToken` curve lps
    curve_lps = [
        trops.contract(r.treasury_tokens.badgerWBTC_f),
        trops.contract(r.treasury_tokens.bveCVX_CVX_f),
    ]
    for lp in curve_lps:
        # NOTE: one of the lp, its the pool itself
        pool_addr = (
            lp.address if "add_liquidity" in lp.selectors.values() else lp.minter()
        )
        # https://etherscan.io/address/0x24a6108D1985B44130f68550C9c43d556720CF17#code#F1#L102
        module.addFeeTokenCurve(lp, False, pool_addr)

    safe.enableModule(module)

    trops.post_safe_tx()


def add_member():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)
    upkeep_manager = techops.contract(r.badger_wallets.upkeep_manager)

    upkeep_manager.addMember(
        r.safe_modules.treasury_ops_multisig.fee_collector,
        "FeeCollectorModule",
        # gas figure ref: https://github.com/Badger-Finance/badger-multisig/issues/1198#issuecomment-1485062644
        2_000_000,
        0,
    )

    techops.post_safe_tx()
