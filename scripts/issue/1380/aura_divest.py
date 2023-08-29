from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# Contracts
SAFE = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
VAULT = r.badger_wallets.treasury_vault_multisig
LOCKER = SAFE.contract(r.aura.vlAURA)

# Tokens
AURA = SAFE.contract(r.treasury_tokens.AURA)
WETH = SAFE.contract(r.treasury_tokens.WETH)

# artificially create slippage on the quoted price from cowswap
COEF = 0.98
# time after which cowswap order expires
DEADLINE = 60 * 60 * 3


def main():
    SAFE.init_cow(prod=True)

    # Get current unlockable balance
    unlockable = LOCKER.lockedBalances(SAFE.account)[1]
    current_balance = AURA.balanceOf(SAFE.account)

    if unlockable > 0:
        # Process expired locks without relocking
        LOCKER.processExpiredLocks(False)
        assert AURA.balanceOf(SAFE.account) == current_balance + unlockable

        # Sell unlocked AURA for ETH
        SAFE.cow.allow_relayer(AURA, unlockable)
        SAFE.cow.market_sell(
            AURA, WETH, unlockable, deadline=DEADLINE, coef=COEF, destination=VAULT
        )

        SAFE.post_safe_tx()
