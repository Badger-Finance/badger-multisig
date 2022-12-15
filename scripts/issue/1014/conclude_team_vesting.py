from great_ape_safe import GreatApeSafe
from helpers.addresses import r


TO_DISTRIBUTE = 728820123211567732115678 - 2e18

recipient_amounts = {
    "0x4300dB1B4D8F417Ccf6672CEa75174b39d9A5e4e": TO_DISTRIBUTE * 0.6,
    "0xECE2C248630C7eE5A1A2C2Ea780233b615E6862D": TO_DISTRIBUTE * 0.4,
}

safe = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
badger = safe.contract(r.treasury_tokens.BADGER)


def main():
    safe.take_snapshot(tokens=[badger])

    for recipient, amount in recipient_amounts.items():
        # test transfer of 1 BADGER first
        badger.transfer(recipient, 1e18)
        badger.transfer(recipient, amount)

    safe.print_snapshot()
    safe.post_safe_tx()
