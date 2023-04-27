from brownie import accounts, interface

from helpers.addresses import r


def sim_exec(safe):
    # bit naive as it is only executes the last tx in safe.transactions
    # NOTE: it is possible to execute a tx while older ones remain unconfirmed!
    last_nonce = safe.transactionCount() - 1
    if safe.transactions(last_nonce)[-1]:
        # print("executed!")
        return
    for signer in safe.getOwners():
        # loop through owners until a signer is found that hasnt signed yet
        if signer in safe.getConfirmations(last_nonce):
            continue
        # print("nonce:", last_nonce)
        # print("tx:", safe.transactions(last_nonce))
        # print("confirmations:", safe.getConfirmations(last_nonce))
        # print("signer:", signer)
        safe.confirmTransaction(last_nonce, {"from": accounts.at(signer, force=True)})
        break
    sim_exec(safe)


# for sim purposes
SIGNER = accounts.at(r.badger_wallets.ops_deployer4, force=True)

# actual poster has to load hot signer account here
# SIGNER = accounts.load('0x123')


def sim():
    main(True)


def main(sim=False):
    dev_old = interface.IMultisigWalletWithDailyLimit(
        r.badger_wallets.dev_multisig_deprecated
    )
    dev = r.badger_wallets.dev_multisig
    owners_before = dev_old.getOwners()

    # add dev msig to owners
    calldata = dev_old.addOwner.encode_input(dev)
    dev_old.submitTransaction(dev_old, 0, calldata, {"from": SIGNER})
    if sim:
        sim_exec(dev_old)
        assert dev in dev_old.getOwners()

    # set threshold to 1
    calldata = dev_old.changeRequirement.encode_input(1)
    dev_old.submitTransaction(dev_old, 0, calldata, {"from": SIGNER})
    if sim:
        sim_exec(dev_old)
        assert dev_old.required() == 1

    # remove all other owners except for SIGNER
    for owner in owners_before:
        calldata = dev_old.removeOwner.encode_input(owner)
        if owner == SIGNER:
            continue
        dev_old.submitTransaction(dev_old, 0, calldata, {"from": SIGNER})
        # no need to sim exec since with threshold==1 submit==confirm==execute

    # remove SIGNER as an owner
    calldata = dev_old.removeOwner.encode_input(SIGNER)
    dev_old.submitTransaction(dev_old, 0, calldata, {"from": SIGNER})

    if sim:
        assert len(dev_old.getOwners()) == 1
        assert dev_old.getOwners()[0] == dev
        assert dev_old.required() == 1
