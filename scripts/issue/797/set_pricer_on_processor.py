from brownie import interface, accounts
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from rich.console import Console

C = Console()

DEV = registry.eth.badger_wallets.dev_multisig
PROCESSOR = registry.eth.aura_bribes_processor
PRICER = registry.eth.on_chain_pricing_mainnet_lenient

# Simulation
COEF = 0.9825
DEADLINE = 60 * 60 * 3
BRIBE_TOKEN = registry.eth.bribe_tokens_claimable_graviaura.DFX
WHALE = "0xA4fc358455Febe425536fd1878bE67FfDBDEC59a"
AMOUNT = 1000e18

def main(simulation="false"):
    safe = GreatApeSafe(DEV)
    safe.init_badger()

    processor = safe.contract(PROCESSOR)

    processor.setPricer(PRICER)
    assert processor.pricer() == PRICER

    # Simulate 
    if simulation == "true":
        weth = interface.IWETH9(registry.eth.treasury_tokens.WETH, owner=safe.account)
        whale = accounts.at(WHALE, force=True)
        token = safe.contract(BRIBE_TOKEN)
        settlement = safe.contract(processor.SETTLEMENT())

        token.transfer(PROCESSOR, AMOUNT, {"from": whale})
        assert token.balanceOf(PROCESSOR) == AMOUNT

        safe.init_badger()
        safe.init_cow(prod=False)

        order_payload, order_uid = safe.badger.get_order_for_processor(
            processor,
            sell_token=token,
            mantissa_sell=AMOUNT,
            buy_token=weth,
            deadline=DEADLINE,
            coef=COEF,
            prod=False,
        )
        processor.sellBribeForWeth(order_payload, order_uid, {"from": accounts.at(processor.manager(), force=True)})

        assert settlement.preSignature(order_uid) > 0

    safe.post_safe_tx()
