from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

C = Console()

VOTER = r.badger_wallets.treasury_voter_multisig
TROPS = r.badger_wallets.treasury_ops_multisig
VAULT = r.badger_wallets.treasury_vault_multisig

# Tokens
CVX = r.treasury_tokens.CVX
CVXCRV = r.treasury_tokens.cvxCRV
USDC = r.treasury_tokens.USDC

# Vaults
BVECVX = r.sett_vaults.bveCVX
BCVXCRV = r.sett_vaults.bcvxCRV
BVECVXCVXF = r.sett_vaults.bbveCVX_CVX_f

# Cow params
COEF = 0.95
DEADLINE = 60 * 60 * 12


def transfer_fees_to_voter():
    """
    Transfer CVX and cvxCRV accumulated fees from Trops to Voter
    """
    safe = GreatApeSafe(TROPS)

    # Contracts
    cvx = safe.contract(CVX)
    cvxcrv = safe.contract(CVXCRV)
    cvx.transfer(VOTER, cvx.balanceOf(TROPS))
    cvxcrv.transfer(VOTER, cvxcrv.balanceOf(TROPS))

    safe.post_safe_tx()


def main():
    """
    0. Transfer CVX and cvxCRV accumulated fees from Trops to Voter
    ----------------------------------------------------------------
    1. Withdraw from Badger bveCVX/CVX vault from Voter
    2. Withdraw from bveCVX/CVX-f pool on Curve from Voter
    3. Claim Badger rewards for Voter
    4. Withdraw from bveCVX and bcvxCRV
    5. Sell CVX and cvxCRV for USDC with Vault as destination
    """

    safe = GreatApeSafe(VOTER)
    safe.init_badger()
    safe.init_curve()
    safe.init_cow(True)

    # Contracts
    cvx = safe.contract(CVX)
    cvxcrv = safe.contract(CVXCRV)
    usdc = safe.contract(USDC)
    bvecvx = safe.contract(BVECVX)
    bcvxcrv = safe.contract(BCVXCRV)
    bvecvxcvxf = safe.contract(BVECVXCVXF)
    bvecvxcvxf_lp = safe.contract(bvecvxcvxf.token())

    safe.take_snapshot([cvx, cvxcrv, usdc, bvecvx, bcvxcrv, bvecvxcvxf, bvecvxcvxf_lp])

    # Withdraw from Badger bveCVX/CVX vault
    bvecvxcvxf.withdrawAll()

    # Withdraw from bveCVX/CVX-f pool on Curve according to current distribution
    cvx_balance_before = cvx.balanceOf(VOTER)
    bvecvx_balance_before = bvecvx.balanceOf(VOTER)
    lp_balance = bvecvxcvxf_lp.balanceOf(VOTER)
    safe.curve.withdraw(bvecvxcvxf_lp, lp_balance)
    assert cvx.balanceOf(VOTER) > cvx_balance_before
    assert bvecvx.balanceOf(VOTER) > bvecvx_balance_before

    # Claim Badger rewards
    bcvxcrv_balance_before = bcvxcrv.balanceOf(VOTER)
    safe.badger.claim_all()
    assert bcvxcrv.balanceOf(VOTER) > bcvxcrv_balance_before

    # Withdraw from bveCVX and bcvxCRV
    bvecvx.withdrawAll()
    bcvxcrv.withdrawAll()

    safe.print_snapshot()

    # Sell CVX and cvxCRV for USDC
    safe.cow.market_sell(
        cvx, usdc, cvx.balanceOf(safe), deadline=DEADLINE, coef=COEF, destination=VAULT
    )
    safe.cow.market_sell(
        cvxcrv,
        usdc,
        cvxcrv.balanceOf(safe),
        deadline=DEADLINE,
        coef=COEF,
        destination=VAULT,
    )

    safe.post_safe_tx()
