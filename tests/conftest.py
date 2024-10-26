import pytest
from brownie import accounts, interface
from brownie_tokens import MintableForkToken
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


@pytest.fixture(scope="module", autouse=True)
def shared_setup(module_isolation):
    pass


@pytest.fixture
def safe():
    return GreatApeSafe(accounts[9].address)


@pytest.fixture
def dev():
    return GreatApeSafe(registry.eth.badger_wallets.dev_multisig)


@pytest.fixture
def techops():
    return GreatApeSafe(registry.eth.badger_wallets.techops_multisig)


@pytest.fixture
def vault():
    return GreatApeSafe(registry.eth.badger_wallets.treasury_vault_multisig)


@pytest.fixture
def ibbtc_msig():
    return GreatApeSafe(registry.eth.badger_wallets.ibbtc_multisig)


@pytest.fixture
def voter_msig():
    return GreatApeSafe(registry.eth.badger_wallets.treasury_voter_multisig)


@pytest.fixture
def USDC(safe):
    usdc = interface.IFiatTokenV2_1(
        registry.eth.treasury_tokens.USDC, owner=safe.account
    )
    usdc_mintable = MintableForkToken(usdc.address, owner=safe.account)
    usdc_mintable._mint_for_testing(safe, 1_000_000 * 10 ** usdc.decimals())
    return usdc


@pytest.fixture
def dai(safe):
    dai = interface.IDai(registry.eth.treasury_tokens.DAI, owner=safe.account)
    dai_mintable = MintableForkToken(dai.address, owner=safe.account)
    dai_mintable._mint_for_testing(safe, 1_000_000 * 10 ** dai.decimals())
    return dai
