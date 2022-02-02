from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import Wei, interface

recipient = registry.eth.badger_wallets.treasury_ops_multisig


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)

    safe.take_snapshot(
        tokens=[
            registry.eth.treasury_tokens.BADGER,
            registry.eth.treasury_tokens.CRV,
            registry.eth.treasury_tokens.CVX,
            registry.eth.sett_vaults.bcrvIbBTC,
            registry.eth.treasury_tokens.crvMIM,
            registry.eth.treasury_tokens.crv3pool,
        ]
    )

    # tokens transfer to process
    badger = safe.contract(registry.eth.treasury_tokens.BADGER)
    crv = safe.contract(registry.eth.treasury_tokens.CRV)
    cvx = safe.contract(registry.eth.treasury_tokens.CVX)
    bcrvIbBTC = safe.contract(registry.eth.sett_vaults.bcrvIbBTC)

    badger.transfer(recipient, Wei("15000 ether"))
    crv.transfer(recipient, crv.balanceOf(safe))
    cvx.transfer(recipient, cvx.balanceOf(safe))
    bcrvIbBTC.transfer(recipient, Wei("25 ether"))

    # tree top-uo
    badger.transfer(
        registry.eth.badger_wallets.badgertree, Wei("79676.9320625347 ether")
    )
    # transfer to remBADGER sett, covers 2w
    badger.transfer(registry.eth.sett_vaults.remBADGER, Wei("11538.461538 ether"))

    # wd mim3pool -> 3pool
    safe.init_curve()

    mim3lp = interface.IStableSwap2Pool(
        registry.eth.treasury_tokens.crvMIM, owner=safe.address
    )
    crv3lp = interface.ICurveLP(registry.eth.treasury_tokens.crv3pool)

    safe.curve.withdraw_to_one_coin(mim3lp, mim3lp.balanceOf(safe), crv3lp)

    safe.post_safe_tx()
