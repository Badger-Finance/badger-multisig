from great_ape_safe import GreatApeSafe
from helpers.addresses import r


PROP_ID = ""
TIMESTAMP = 0
CHOICE = {"80/20 BADGER/WBTC": 1}


def main():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    voter.init_snapshot(PROP_ID)
    voter.snapshot.create_payload_hash(timestamp=TIMESTAMP, choice=CHOICE)
