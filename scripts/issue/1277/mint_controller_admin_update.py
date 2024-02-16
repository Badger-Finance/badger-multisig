from brownie import accounts, chain

from eth_abi import encode_abi

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main(verify_future_state=True):
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)

    # contracts
    controller = safe.contract(r.GatedMiniMeController)
    timelock_gov = safe.contract(r.governance_timelock)

    # tkns
    badger = safe.contract(r.treasury_tokens.BADGER)
    dai = safe.contract(r.treasury_tokens.DAI)

    controller.transferOwnership(timelock_gov)

    if verify_future_state:
        tl_gov = accounts.at(r.governance_timelock, force=True)

        # mint
        controller.mint(100e18, {"from": tl_gov})

        assert badger.balanceOf(tl_gov) == 100e18

        # ensure tokens can be move from tl
        badgerBalBefore = badger.balanceOf(safe)

        calldata = encode_abi(
            ["address", "uint256"],
            [safe.address, int(100e18)],
        )
        eta = chain.time() + int(3 * 60 * 60 * 24)

        timelock_gov.queueTransaction(
            badger, 0, "transfer(address,uint256)", calldata, eta
        )

        chain.mine(timestamp=eta + 1)
        timelock_gov.executeTransaction(
            badger, 0, "transfer(address,uint256)", calldata, eta
        )

        assert badger.balanceOf(safe) == badgerBalBefore + 100e18

        # claim tokens
        bal_in_minime = dai.balanceOf(badger)

        controller.claimTokens(r.treasury_tokens.DAI, {"from": tl_gov})

        assert dai.balanceOf(tl_gov) == bal_in_minime

        # disable minting
        controller.disableMinting({"from": tl_gov})

        assert controller.mintingEnabled() == False

        # transfer ownership
        controller.transferOwnership(
            r.badger_wallets.treasury_vault_multisig, {"from": tl_gov}
        )

        assert controller.owner() == r.badger_wallets.treasury_vault_multisig

        # erc20 basic samples
        holder_one = accounts.at(r.badger_wallets.treasury_vault_multisig, force=True)
        holder_two = accounts.at(r.badger_wallets.treasury_ops_multisig, force=True)

        # check basic transfer and balance updates
        holder_one_bal_before = badger.balanceOf(holder_one)
        holder_two_bal_before = badger.balanceOf(holder_two)

        badger.transfer(holder_two, 5e18, {"from": holder_one})

        assert badger.balanceOf(holder_two) == holder_two_bal_before + 5e18
        assert badger.balanceOf(holder_one) == holder_one_bal_before - 5e18

    if not verify_future_state:
        safe.post_safe_tx()
    else:
        safe.post_safe_tx(skip_preview=True)
