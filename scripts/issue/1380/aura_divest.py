from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from rich.console import Console

C = Console()

# Contracts
SAFE = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
VAULT = r.badger_wallets.treasury_vault_multisig
TROPS = r.badger_wallets.treasury_ops_multisig
LOCKER = SAFE.contract(r.aura.vlAURA)
GRAVIAURA = SAFE.contract(r.sett_vaults.graviAURA)

# Tokens
AURA = SAFE.contract(r.treasury_tokens.AURA)
WETH = SAFE.contract(r.treasury_tokens.WETH)
AURABAL = SAFE.contract(r.treasury_tokens.AURABAL)


# artificially create slippage on the quoted price from cowswap
COEF = 0.98
# time after which cowswap order expires
DEADLINE = 60 * 60 * 24


def main(claim_rewards=False):
    SAFE.init_cow(prod=True)

    # Since the upKeep was shutdown, rewards must be manually claimed
    rewards = LOCKER.claimableRewards(SAFE.account)[0][1]
    if rewards > 0 and claim_rewards:
        LOCKER.getReward(SAFE.account)
        aurabal_balance = AURABAL.balanceOf(SAFE.account)

        # Transfer rewards to Trops
        AURABAL.transfer(TROPS, aurabal_balance)
        C.print(
            f"[green]{aurabal_balance/1e18} AURABAL were claimed and transfered to trops[/green]"
        )

        # Since the upKeep was shutdown, graviAURA must be manually withdrawn
        # Only doing every once in a while to clean-up along with the rewards
        if GRAVIAURA.balanceOf(SAFE.account) > 0:
            GRAVIAURA.withdrawAll()

    # Get current unlockable balance
    unlockable = LOCKER.lockedBalances(SAFE.account)[1]
    current_aura_balance = AURA.balanceOf(SAFE.account)

    if unlockable > 0:
        # Process expired locks without relocking
        LOCKER.processExpiredLocks(False)
        aura_balance = AURA.balanceOf(SAFE.account)
        assert aura_balance == current_aura_balance + unlockable

        # Sell unlocked AURA for ETH
        SAFE.cow.allow_relayer(AURA, aura_balance)
        SAFE.cow.market_sell(
            AURA, WETH, aura_balance, deadline=DEADLINE, coef=COEF, destination=VAULT
        )

        C.print(
            f"[green]{aura_balance/1e18} AURA were claimed and sold for wETH[/green]"
        )

        # Only execute when unlockable available - rewards can wait until next epoch
        SAFE.post_safe_tx()
