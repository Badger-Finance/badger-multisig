from brownie import interface
from eth_abi import encode_abi
from rich.console import Console

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


DEV = GreatApeSafe(r.badger_wallets.dev_multisig)
DEV.init_badger()
DEV_PROXY_ADMIN = interface.IProxyAdmin(
    r.badger_wallets.devProxyAdmin, owner=DEV.badger.timelock
)
TROPS = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
GEYSER = DEV.contract(r.badger_wallets.uniswap_rewards)
BADGER = DEV.contract(r.treasury_tokens.BADGER)
AURA = DEV.contract(r.treasury_tokens.AURA)
USDC = DEV.contract(r.treasury_tokens.USDC)
WETH = DEV.contract(r.treasury_tokens.WETH)
WBTC = DEV.contract(r.treasury_tokens.WBTC)
ULP = DEV.contract(r.treasury_tokens.uniWbtcBadger)

NEW_LOGIC = '0xf8C383A50984Ea50D9e343572F49a09152b3e674'
DUMP_DIR = 'data/badger/timelock/upgrade_uni_lp_geyser/'

C = Console()


def queue():
    # queue the upgrade
    DEV.badger.queue_timelock(
        target_addr=DEV_PROXY_ADMIN.address,
        signature='upgrade(address,address)',
        data=encode_abi(['address', 'address'], [GEYSER.address, NEW_LOGIC]),
        dump_dir=DUMP_DIR,
        delay_in_days=4,
    )


def sim():
    main(sim=True)


def main(sim=None):
    tokens = [BADGER, AURA, USDC, WETH, WBTC, ULP]
    DEV.take_snapshot(tokens)
    TROPS.take_snapshot(tokens)

    # save balances
    prev_balance = {}
    for token in tokens:
        prev_balance[token.address] = token.balanceOf(GEYSER)

    # save storage vars
    attributes = {}
    for attr in GEYSER.signatures:
        try:
            attributes[attr] = getattr(GEYSER, attr).call()
        except:
            C.print(f'[red]error storing {attr}[/red]')

    if sim:
        # simulate the upgrade
        DEV_PROXY_ADMIN.upgrade(GEYSER, NEW_LOGIC)
    else:
        # execute the upgrade
        DEV.badger.execute_timelock(DUMP_DIR)

    # assert balances
    for token in tokens:
        assert prev_balance[token.address] == token.balanceOf(GEYSER)
        C.print(f'[green]asserted balanceOf for {token.address}[/green]')

    # assert storage vars
    for attr in GEYSER.signatures:
        try:
            assert attributes[attr] == getattr(GEYSER, attr).call()
            C.print(f'[green]asserted {attr}[/green]')
        except:
            pass

    # recover the badger from the geyser
    GEYSER.recoverERC20(BADGER, BADGER.balanceOf(GEYSER))

    # sweep all assets to trops; dev shouldnt be holding these
    BADGER.transfer(TROPS, BADGER.balanceOf(DEV))
    AURA.transfer(TROPS, AURA.balanceOf(DEV))
    USDC.transfer(TROPS, USDC.balanceOf(DEV))
    WETH.transfer(TROPS, WETH.balanceOf(DEV))
    WBTC.transfer(TROPS, WBTC.balanceOf(DEV))

    DEV.print_snapshot()
    TROPS.print_snapshot()

    if not sim:
        DEV.post_safe_tx(call_trace=True)
