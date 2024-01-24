from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import accounts

# flag
PROD = False
COEF = 0.99
DEADLINE = 60 * 60 * 4

# funding figures (treasury)
TREASURY_COUNCIL_YEARLY_FUNDING = 300_000e6
COUNCILLOR_PAYMENT_COVERED = 2927.777777777777784336e6

# funding figure (association)
ASSOC_Q1_FUNDING_STABLES = 1_154_918
ASSOC_Q1_FUNDING_BADGER = 137_706e18

# testing
USDC_WHALE = "0xD6153F5af5679a75cC85D8974463545181f48772"


def sell_stable_for_usdc():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    vault.init_cow(prod=PROD)

    # tokens
    usdc = vault.contract(r.treasury_tokens.USDC)
    dai = vault.contract(r.treasury_tokens.DAI)
    lusd = vault.contract(r.treasury_tokens.LUSD)

    # 1. sell $dai for $usdc
    vault.cow.market_sell(
        asset_sell=dai,
        asset_buy=usdc,
        mantissa_sell=ASSOC_Q1_FUNDING_STABLES * 10 ** dai.decimals(),
        deadline=DEADLINE,
        coef=COEF,
    )

    # 2. sell $lusd (full balance) for $usdc
    vault.cow.market_sell(
        asset_sell=lusd,
        asset_buy=usdc,
        mantissa_sell=lusd.balanceOf(vault),
        deadline=DEADLINE,
        coef=COEF,
    )

    vault.post_safe_tx()


def assoc_and_council_funding(sim=False):
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    payments = GreatApeSafe(r.badger_wallets.payments_multisig_2024)

    # tokens
    usdc = vault.contract(r.treasury_tokens.USDC)
    badger = vault.contract(r.treasury_tokens.BADGER)

    # for testing purposes (USDC acquisition)
    if sim:
        usdc_whale = accounts.at(USDC_WHALE, force=True)
        usdc.transfer(vault.account, 2_000_000e6, {"from": usdc_whale})

    vault.take_snapshot([usdc, badger])
    payments.take_snapshot([usdc, badger])

    # contracts
    llamapay = vault.contract(r.llamapay)

    # 1. transfer funding to assoc. wallet
    usdc.transfer(
        payments.account,
        ASSOC_Q1_FUNDING_STABLES * 10 ** usdc.decimals(),
    )
    badger.transfer(payments.account, ASSOC_Q1_FUNDING_BADGER)

    # 2. top-up yearly funding for treasury council
    usdc.approve(llamapay, TREASURY_COUNCIL_YEARLY_FUNDING)
    llamapay.deposit(TREASURY_COUNCIL_YEARLY_FUNDING)
    # Accounting on LlamaPay is done in 1e20 units (https://etherscan.io/address/0x3e67cc2c7fff86d9870db9d02c43e789b52fb296#code#F1#L218)
    assert llamapay.balances(
        vault.account
    ) / 1e20 == TREASURY_COUNCIL_YEARLY_FUNDING / (10 ** usdc.decimals())

    # 3. transfer $usdc to councillors members for covering payment before stream initialisation this month
    usdc.transfer(
        r.badger_wallets.treasury_councillors.councillor1, COUNCILLOR_PAYMENT_COVERED
    )
    usdc.transfer(
        r.badger_wallets.treasury_councillors.councillor2, COUNCILLOR_PAYMENT_COVERED
    )
    usdc.transfer(
        r.badger_wallets.treasury_councillors.councillor3, COUNCILLOR_PAYMENT_COVERED
    )
    usdc.transfer(
        r.badger_wallets.treasury_councillors.councillor4, COUNCILLOR_PAYMENT_COVERED
    )
    usdc.transfer(
        r.badger_wallets.treasury_councillors.councillor5, COUNCILLOR_PAYMENT_COVERED
    )

    payments.print_snapshot()
    vault.print_snapshot()
    vault.post_safe_tx()
