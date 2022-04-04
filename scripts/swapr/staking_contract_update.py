from brownie import interface, accounts, Contract, web3
from helpers.addresses import ADDRESSES_ARBITRUM

dev_multisig = ADDRESSES_ARBITRUM["badger_wallets"]["dev_multisig_deprecated"]
strategies = ADDRESSES_ARBITRUM["strategies"]
staking_contracts = ADDRESSES_ARBITRUM["swapr_staking_contracts"]


# REPLACE HERE THE NAME OF YOUR ADDRESS WITH THE RIGHTS
ACCOUNT_TO_LOAD = ""


def main(simulation="false"):

    if simulation == "true":
        dev = accounts.at(dev_multisig, force=True)
    else:
        dev = accounts.load(ACCOUNT_TO_LOAD)

    safe = interface.IMultisigWalletWithDailyLimit(dev_multisig)

    for key in [
        "native.DXSSwaprWeth",
        "native.DXSWbtcWeth",
        "native.DXSBadgerWeth",
        "native.DXSIbbtcWeth",
    ]:
        strategy = Contract(strategies[key])

        if strategy.stakingContract() == web3.toChecksumAddress(staking_contracts[key]):
            continue

        old_staking_contract = interface.IERC20StakingRewardsDistribution(
            strategy.stakingContract()
        )
        staking_contract = interface.IERC20StakingRewardsDistribution(
            staking_contracts[key]
        )

        assert strategy.want() == staking_contract.stakableToken()
        assert (
            old_staking_contract.endingTimestamp()
            == staking_contract.startingTimestamp()
        )

        # Make sure the staking contracts are accurate
        encode_input = strategy.setStakingContract.encode_input(
            staking_contract.address
        )

        print(f"{key} ({strategy.address})")
        print(f"==== calldata={encode_input} ==== \n")

        # safe.submitTransaction(strategy.address, 0, encode_input, {"from": dev})
