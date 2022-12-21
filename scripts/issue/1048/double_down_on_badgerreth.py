from decimal import Decimal

from pycoingecko import CoinGeckoAPI
from web3 import Web3

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


AMNT_ETH = 932.96e18
SLIPPAGE = 0.98


def main():
    treasury = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    reth = treasury.contract(r.treasury_tokens.RETH)
    weth = treasury.contract(r.treasury_tokens.WETH)
    badger = treasury.contract(r.treasury_tokens.BADGER)
    bpt_badgerreth = treasury.contract(r.balancer.B_50_BADGER_50_RETH)
    bpt_wethreth = treasury.contract(r.balancer.B_50_WETH_50_RETH)
    rocket_deposit = treasury.contract(r.rocket_pool.deposit)
    rocket_storage = treasury.contract(r.rocket_pool.storage)
    rocket_vault = treasury.contract(
        rocket_storage.getAddress(
            Web3.solidityKeccak(["bytes32"], [b"contract.address" + b"rocketVault"])
        )
    )
    rocket_settings = treasury.contract(
        rocket_storage.getAddress(
            Web3.solidityKeccak(
                ["bytes32"], [b"contract.address" + b"rocketDAOProtocolSettingsDeposit"]
            )
        )
    )

    trops.take_snapshot([weth])
    treasury.take_snapshot([reth, weth, badger, bpt_badgerreth])
    treasury.init_balancer()

    reth_needed = AMNT_ETH - (reth.balanceOf(treasury) * reth.getExchangeRate() / 1e18)

    # how much reth can we get natively?
    # ref: https://github.com/rocket-pool/rocketpool/blob/93f794b8d4aabe4c3e3c64170c475d337bdb9d28/contracts/contract/deposit/RocketDepositPool.sol#L80
    reth_natively = (
        rocket_settings.getMaximumDepositPoolSize()
        - rocket_vault.balanceOf(b"rocketDepositPool")
    )
    if reth_natively >= reth_needed:
        weth.withdraw(reth_natively)
        rocket_deposit.deposit({"value": reth_natively})
    else:
        treasury.balancer.swap(weth, reth, reth_needed, pool=bpt_wethreth)

    reth_to_deposit = reth.balanceOf(treasury) * SLIPPAGE

    prices = CoinGeckoAPI().get_price(["rocket-pool-eth", "badger-dao"], "usd")
    badger_to_deposit = Decimal(reth_to_deposit) * Decimal(
        prices["rocket-pool-eth"]["usd"] / prices["badger-dao"]["usd"]
    )

    treasury.balancer.deposit_and_stake(
        [badger, reth],
        [badger_to_deposit, reth_to_deposit],
        pool=bpt_badgerreth,
        stake=False,
    )

    # send remaining weth to trops for gas operations
    weth.transfer(trops, weth.balanceOf(treasury))

    trops.print_snapshot()

    treasury.post_safe_tx()
