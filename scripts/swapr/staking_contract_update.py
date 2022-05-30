from brownie import interface, web3
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

SAFE = GreatApeSafe(registry.arbitrum.badger_wallets.dev_multisig)

strategies = registry.arbitrum.strategies
staking_contracts = registry.arbitrum.swapr_staking_contracts

def main():
    for key in [
        "native.DXSSwaprWeth",
        "native.DXSWbtcWeth",
        "native.DXSBadgerWeth",
        "native.DXSIbbtcWeth",
    ]:
        strategy = SAFE.contract(strategies[key])

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
        strategy.setStakingContract(
            staking_contract.address
        )

    SAFE.post_safe_tx()
