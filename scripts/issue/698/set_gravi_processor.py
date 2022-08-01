from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from scripts.badger.process_bribes_graviaura import claim_and_sell_for_weth

NEW_PROCESSOR = r.aura_bribes_processor

def main(simulation="false"):
    safe = GreatApeSafe(r.badger_wallets.dev_multisig)
    safe.init_badger()

    processor = safe.contract(NEW_PROCESSOR)
    assert processor.manager() == r.badger_wallets.techops_multisig

    safe.badger.strat_graviaura.setBribesProcessor(NEW_PROCESSOR)

    if simulation == "true":
        # Call was currently broken with previous version since the `getHash` function had 
        # the wrong encoding. Calling after switching processor to confirm that the flow will
        # work properly.
        claim_and_sell_for_weth()
    else:
        safe.post_safe_tx(call_trace=True)
