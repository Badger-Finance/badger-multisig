from great_ape_safe import GreatApeSafe
from helpers.addresses import r

COUNCIL = {
    "0x2797ff1C04A20ABEc5B8bC2a5b76A41D70d097C3": 795.00,
    "0xB2043AFEC208F170f6Fb8A88284330c879105fF7": 398.00,
    "0xD798428e860465E08B522f8440f707593E6d22C6": 398.00,
    "0x567244C8E8dff152bE7A276DCD05AA332767386E": 398.00,
    "0xdE0AEf70a7ae324045B7722C903aaaec2ac175F5": 398.00,
    "0x565871756d14424000e3a052e270eba6f1ec5e88": 795.00,
    "0xB5c46131B4d8d13e4c0E476B9A2Ea5b43945891e": 398.00,
    "0xF2Cf9d7513A2F6EAAe9d82b95B3c40D0efebE33B": 398.00
}

def main():
    vault = GreatApeSafe(r.badger_wallets.treasury_vault_multisig)
    badger = vault.contract(r.treasury_tokens.BADGER)

    for member, amount in COUNCIL.items():
        badger.transfer(member, amount*1e18)

    vault.post_safe_tx()