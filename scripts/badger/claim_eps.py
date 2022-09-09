import requests
import json
from great_ape_safe import GreatApeSafe

from helpers.addresses import registry

# addresses involved
multisigAddressDeprecated = registry.bsc.badger_wallets.dev_multisig_deprecated
multisigAddress = registry.bsc.badger_wallets.dev_multisig
# tried to grab Created events from the factory (TODO!) - err persist on today test seems and issue with bsc - web3
# merkle_airdrop_factory = "0xF403C135812408BFbE8713b5A23a04b3D48AAE31"
eps_address = registry.bsc.airdropable_tokens.EPS

url_old_multisig = f"https://www.convexfinance.com/api/eps/address-airdrop-info?address={multisigAddressDeprecated}"
url_new_multisig = f"https://www.convexfinance.com/api/eps/address-airdrop-info?address={multisigAddress}"

# eligible airdrop periods
last_weeks = [
    "2021-07-01",
    "2021-07-08",
    "2021-07-15",
    "2021-07-22",
    "2021-07-29",
    "2021-08-05",
    "2021-08-12",
    "2021-08-19",
    "2021-08-26",  # note: till here is old-multi period!
    # "2021-09-02",
    # "2021-09-09",
    # "2021-09-16",
    # "2021-09-23"
    # "2021-09-30"
    # "2021-10-07",
    # "2021-10-14",
    # "2021-10-21",
    # "2021-10-28",
    # "2021-11-04",
    # "2021-11-11",
    # "2021-11-18",
    # "2021-11-25"
    # "2021-12-02",
    # "2021-12-09",
    # "2021-12-16",
    # "2021-12-23",
    # "2021-12-30",
    # "2022-01-06",
    # "2022-01-13",
    # "2022-01-20",
    # "2022-01-27",
    # "2022-02-03",
    # "2022-02-10",
    # "2022-02-17",
    # "2022-02-24",
    "2022-03-03",
    "2022-03-10",
    "2022-03-17",  # last eps airdrop week, no 52w
]

# claim contracts for the old multisig
merkle_airdrops_old = [
    "0xf140b370Ae1238Add424d3F9B7ED409dAdB7E238",
    "0x81E47381aA927ffA2138263e50716B1C573B0Eb5",
    "0xc789F8fc2dD7D14DFFEA9e3D7e78BDe43ea9F439",
    "0xA0f7B26ccDc490ef9E5CedB7e956351aA4bE5B1B",
    "0xcbCa4Cd79aF621184DDc14CDC6C43E37Db780470",
    "0xA988E0B94F0b187474ff45D7ca9F1ecbe80824E7",
    "0x4BF0172272470125486CEaD15718f9B7B5185E02",
    "0x37a0f7cac3b4AaDFc4347cCd4c890604AC3DAfDa",
    "0x3d7F3140aCc4176cf510008A5773a7Be7cDe0fBA",
]

# claims contracts for new multisig into new address from 2021-09-02
merkle_airdrops_new = [
    # "0x0d59D439a4466Ef2b22d50d11eABcCbd54f42052",
    # "0x37E18aaB177E169dAA33D24F26b8ab3A6ccf0c0e",
    # "0x1639f30b195d25b254Cc128Ac9d864707D30Df00",
    # "0xfb0e623295C0599DECAf1d40046D728D6e7a58E9",
    # "0xF76Ab4382d3737e6199812fbDDAF459e250EcEdc"
    # "0xE8aA47084509f1927946354a079279644Ba6fb1F",
    # "0x79b89544C3f6cba5e780814c40d7F669CB7fb20D",
    # "0x565F9554b47Db0772c754fa7A04507aa3b50122E",
    # "0x0Be356523A96D477bc5d7768475f22B56798aDca",
    # "0xF918f28e1E83151c30C9bD99b0B55362754D616C",
    # "0x6e4fA069a6aAbd2529838dEbeD2435e9eAcc1A00",
    # "0xAcf27590F75d8eA23DEc61AE8F23BC75E9De6fFB",
    # "0x6F5741E32570faa767301bB5FB7d892FAd75a12f",
    # "0xAfeb9F72C451c581EA75613C38F4F3d4B29C92c8",
    # "0xf0708696f86d08287e5C1A525E38592D8456676e",
    # "0x03cbDC39a41b0D8d192BaC8E2f92c73Feacc938E",
    # "0xCC093A6E8082aDf38Bb70D9b0aC761c666ff03F4",
    # "0xEa6672757f5D11237EAAf978Da09eC619Ff4e63F",
    # "0x337465264408D0289F9fE4B39277cE62CECa3E01",
    # "0x7eB841876ca7b41e5c5b9E40718214e9Bf8c8186",
    # "0xF776ad79740115B826Ec4BcF3641329852625399",
    # "0x15418C448AE061e8765f4936e2df73C2852BF5e4",
    # "0xa0f8aeD5E5274D03114880bae562828314dE149d",
    # "0x16c0b34Dcee8a57A068500c5364A323B41Bd05cB",
    # "0xDAB55C39784b24C68C20b54f3f14494E208BA215",
    # "0xC850B3F0737B59C47Be7E3b3439C45567A0E95fB",
    "0x158F8f5B1cCb172bb79EAb75ED11eE70083f0e12",
    "0x3EE776BE4Eb9Ac0a7D2DF18052d33fD13abaA476",
    "0xfB5b140b85EC3a05b2E934dbABEc2c9251A3CEaf",
]


# Set explicitily from which addr do you want to claim from True = multisigAddressDeprecated & False = multisigAddress
DEPRECATED_OR_NEW_MULTISIG = False


def main():
    # IMPORTANT: once we moved to use the new gnosis-safe and CONVEX is notified with the new address,
    # the first argument should be set to False to use the new multisig
    # and second argument to True, so only last week is claimed.
    # i.e:  claim(False, True)
    claim()


# will claim: if ´True´ only last week airdrops and ´False´ all pendants airdrops
def claim(
    deprecated_multisig=DEPRECATED_OR_NEW_MULTISIG,
    last_week_or_pendandts=False,
):
    # open safe
    if deprecated_multisig:
        safe = GreatApeSafe(multisigAddressDeprecated)
        # response = requests.get(url_old_multisig) DEV: legacy code for claims
        merkle_airdrop_source = merkle_airdrops_old
        claimable_weeks = last_weeks[:9]
    else:
        safe = GreatApeSafe(multisigAddress)
        # response = requests.get(url_new_multisig) DEV: legacy code for claims
        merkle_airdrop_source = merkle_airdrops_new
        claimable_weeks = last_weeks[9:]

    eps_contract = safe.contract(eps_address)

    DIVISOR = 10 ** eps_contract.decimals()

    # DEV: legacy code for claims
    # json_airdrop_data = response.json()["matchedAirdropData"]
    # airdrop_data_filtered_none = [
    #    entry for entry in json_airdrop_data if entry is not None
    # ]

    TOTAL_CLAIMED = 0
    eps_balance_before = eps_contract.balanceOf(safe.address)

    if last_week_or_pendandts:
        target_json = (
            f"data/Convex_EPS/airdrop/eps/{claimable_weeks[-1]}/drop_proofs.json"
        )
        merkle_airdrop_contract = safe.contract(merkle_airdrop_source[-1])
        with open(target_json) as f:
            last_week_args = json.load(f)["users"][safe.address]
            print(" ====== Claiming arguments for last week: ====== ")
            print(f"\nProof: {last_week_args['proof']}")
            amount_formatted = int(last_week_args["amount"]) / DIVISOR
            print(f"\nAmount: {amount_formatted:,.18f}")

            TOTAL_CLAIMED += amount_formatted
            merkle_airdrop_contract.claim(
                last_week_args["proof"],
                safe.address,
                last_week_args["amount"],
            )
    else:
        for i, date in enumerate(claimable_weeks):
            target_json = (
                f"data/Convex_EPS/airdrop/eps/{date.replace('-', '_')}/drop_proofs.json"
            )
            with open(target_json) as f:
                msig_args_details = json.load(f)["users"][safe.address]
                print(
                    f"\n ====== Claiming arguments for {claimable_weeks[i]} week: ====== "
                )
                print(f"\nProof: {msig_args_details['proof']}")
                amount_formatted = int(msig_args_details["amount"]) / DIVISOR
                print(f"\nAmount: {amount_formatted:,.18f}")

                TOTAL_CLAIMED += amount_formatted
                merkle_airdrop_contract = safe.contract(merkle_airdrop_source[i])
                merkle_airdrop_contract.claim(
                    msig_args_details["proof"],
                    safe.address,
                    msig_args_details["amount"],
                )

    eps_balance_after = eps_contract.balanceOf(safe.address)

    if deprecated_multisig:
        eps_contract.transfer(multisigAddress, eps_balance_after)
        # printout for new multi - extra info
        print(
            f" === IMPORTANT: {(eps_balance_after/DIVISOR):,.18f} were transfer to the new dev multisig at {multisigAddress} === \n"
        )

    print(f"\nTOTAL EPS CLAIMED {TOTAL_CLAIMED:,.18f}")
    print(f"\nEPS balance before claiming: {(eps_balance_before/DIVISOR):,.18f}")
    print(f"\nEPS balance after claiming: {(eps_balance_after/DIVISOR):,.18f}")

    safe.post_safe_tx()
