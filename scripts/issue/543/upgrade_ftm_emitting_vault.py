from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import accounts, interface
from rich.console import Console
from brownie.test.managers.runner import RevertContextManager as reverts

C = Console()

NEW_LOGIC = registry.ftm.logic["theVaultWithoutTree"]
VAULT_ADDRESS = registry.ftm.sett_vaults["bwFTM-WETH-wBTC"]
DEV_PROXY = registry.ftm.badger_wallets.devProxyAdmin
## Account with funds stuck due to integration
USER = "0xB943cdb5622E7Bb26D3E462dB68Ee71D8868C940"

def main(simulation="false"):
    safe = GreatApeSafe(registry.ftm.badger_wallets.dev_multisig)

    vault = interface.ITheVaultWithoutTree(VAULT_ADDRESS, owner=safe.account)
 
    # record current vault information
    prev_strategy = vault.strategy()
    prev_guardian = vault.guardian()
    prev_treasury = vault.treasury()

    prev_badgerTree = vault.badgerTree()

    prev_lifeTimeEarned = vault.lifeTimeEarned()
    prev_lastHarvestedAt = vault.lastHarvestedAt()
    prev_lastHarvestAmount = vault.lastHarvestAmount()
    prev_assetsAtLastHarvest = vault.assetsAtLastHarvest()

    prev_performanceFeeGovernance = vault.performanceFeeGovernance()
    prev_performanceFeeStrategist = vault.performanceFeeStrategist()
    prev_withdrawalFee = vault.withdrawalFee()
    prev_managementFee = vault.managementFee()

    prev_maxPerformanceFee = vault.maxPerformanceFee()
    prev_maxWithdrawalFee = vault.maxWithdrawalFee()
    prev_maxManagementFee = vault.maxManagementFee()

    prev_toEarnBps = vault.toEarnBps()
    prev_totalSupply = vault.totalSupply()
    prev_getPricePerFullShare = vault.getPricePerFullShare()

    ## Check current balances
    initial_shares = vault.balanceOf(USER)
    assert initial_shares > 0

    # Execute upgrade
    proxyAdmin = interface.IProxyAdmin(DEV_PROXY, owner=safe.account)
    proxyAdmin.upgrade(vault.address, NEW_LOGIC)

    ## Confirm balances
    assert initial_shares == vault.balanceOf(USER)

    assert prev_strategy == vault.strategy()
    assert prev_guardian == vault.guardian()
    assert prev_treasury == vault.treasury()

    assert prev_badgerTree == vault.badgerTree()

    assert prev_lifeTimeEarned == vault.lifeTimeEarned()
    assert prev_lastHarvestedAt == vault.lastHarvestedAt()
    assert prev_lastHarvestAmount == vault.lastHarvestAmount()
    assert prev_assetsAtLastHarvest == vault.assetsAtLastHarvest()

    assert prev_performanceFeeGovernance == vault.performanceFeeGovernance()
    assert prev_performanceFeeStrategist == vault.performanceFeeStrategist()
    assert prev_withdrawalFee == vault.withdrawalFee()
    assert prev_managementFee == vault.managementFee()

    assert prev_maxPerformanceFee == vault.maxPerformanceFee()
    assert prev_maxWithdrawalFee == vault.maxWithdrawalFee()
    assert prev_maxManagementFee == vault.maxManagementFee()

    assert prev_toEarnBps == vault.toEarnBps()
    assert prev_totalSupply == vault.totalSupply()
    assert prev_getPricePerFullShare == vault.getPricePerFullShare()

    if simulation == "true":
        # Confirm that user can withdraw
        user = accounts.at(USER, force=True)
        want = interface.ERC20(vault.token())

        initial_bal = want.balanceOf(user)
        vault.withdrawAll({"from": user})

        assert want.balanceOf(user) > initial_bal
        assert vault.balanceOf(user) == 0

    safe.post_safe_tx(post=(simulation!="true"))
