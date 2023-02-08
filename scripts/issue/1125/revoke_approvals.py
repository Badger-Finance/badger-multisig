from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from brownie import multicall, Contract


# https://revoke.cash/address/techops.badgerdao.eth
# https://revoke.cash/address/dev.badgerdao.eth


def main(safe):
    safe = GreatApeSafe(safe)

    # spenders and tokens involved in dev & techops allowances
    spenders = [
        r.sushiswap.routerV2,
        r.uniswap.NonfungiblePositionManager,
        r.uniswap.routerV2,
        "0x4459A591c61CABd905EAb8486Bf628432b15C8b1", # https://etherscan.io/address/0x4459A591c61CABd905EAb8486Bf628432b15C8b1
        "0x111111125434b319222CdBf8C261674aDB56F3ae", # https://etherscan.io/address/0x111111125434b319222CdBf8C261674aDB56F3ae
    ]

    tokens = [
        r.treasury_tokens.BADGER,
        r.treasury_tokens.DIGG,
        r.treasury_tokens.USDC,
        r.treasury_tokens.slpWbtcEth,
        r.treasury_tokens.ibBTC,
        r.treasury_tokens.WBTC,
    ]

    with multicall:
        allowances = {
            Contract(token, owner=safe.account): spender
            for token in tokens
            for spender in spenders
            if Contract(token).allowance(safe, spender) > 0
        }

    for token, spender in allowances.items():
        print(f"Revoking {token.symbol()} allowance for {spender}")
        token.approve(spender, 0)

    safe.post_safe_tx()
