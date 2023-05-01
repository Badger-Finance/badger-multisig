from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)

    # contract
    upkeep_manager = techops.contract(r.badger_wallets.upkeep_manager)

    upkeep_manager.addMember(
        r.safe_modules.treasury_voter.aura_auto_lock,
        "TreasuryVoterModule",
        # gas figure ref: https://automation.chain.link/mainnet/42960818007215227498102337773007812241122867237937589685113781988946396009556
        720_000,
        0,
    )

    techops.post_safe_tx()
