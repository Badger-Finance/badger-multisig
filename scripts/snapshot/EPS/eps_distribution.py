import csv
import datetime
import json
import os
from collections import defaultdict
from datetime import timezone
from fractions import Fraction
from pathlib import Path
from collections import deque

import numpy as np
from brownie import Contract, chain, web3, ZERO_ADDRESS

from helpers.addresses import registry

# Note: EPS distribution every Thrusday 00:00UTC

# setts and swaps contract involved
setts_entitled = [registry.eth.sett_vaults.bcvxCRV]

namings = ["sett_cvxCrv"]

# DAO's msig to blacklist from sett depositors / distribution
badger_tree = registry.eth.badger_wallets.badgertree
dev_multi = registry.eth.badger_wallets.dev_multisig
techops = registry.eth.badger_wallets.techops_multisig
treasury_ops = registry.eth.badger_wallets.treasury_ops_multisig
ibbtc_multisig = registry.eth.badger_wallets.ibbtc_multisig

dev_multi_bsc_latest = registry.bsc.badger_wallets.dev_multisig
# "dev_multisig_deprecated": "0x6DA4c138Dd178F6179091C260de643529A2dAcfe",
url_deprecated = "https://www.convexfinance.com/api/eps/address-airdrop-info?address=0x6DA4c138Dd178F6179091C260de643529A2dAcfe"

# "dev_multisig": "0x329543f0F4BB134A3f7a826DC32532398B38a3fA",
url = "https://www.convexfinance.com/api/eps/address-airdrop-info?address=0x329543f0F4BB134A3f7a826DC32532398B38a3fA"

last_weeks = [
    "2022-02-24",
    "2022-02-17",
    "2022-02-10",
    "2022-02-03",
    # "2022-01-27",
    # "2022-01-20",
    # "2022-01-13",
    # "2022-01-06"
    # "2021-12-30",
    # "2021-12-23",
    # "2021-12-16",
    # "2021-12-09",
    # "2021-12-02"
    # "2021-11-25",
    # "2021-11-18",
    # "2021-11-11",
    # "2021-11-04"
    # "2021-10-28",
    # "2021-10-21",
    # "2021-10-14",
    # "2021-10-07",
    # "2021-09-30",
    # "2021-09-23",
    # "2021-09-16",
    # "2021-09-09",
    # "2021-09-02",
    # "2021-08-26",
    # "2021-08-19",
    # "2021-08-12",
    # "2021-08-05",
    # "2021-07-29",
    # "2021-07-22",
    # "2021-07-15",
    # "2021-07-08",
    # "2021-07-01",
]


def get_depositors_sett(start_block):
    addresses_dict = {}
    """only run if contract are not recognise -> for asset in setts_entitled:
        Contract.from_explorer(asset)"""

    latest = int(chain[-1].number) - 11000

    for idx, addr in enumerate(setts_entitled):
        token_contract = Contract(addr)
        token = web3.eth.contract(token_contract.address, abi=token_contract.abi)
        addresses = set([])
        for height in range(start_block, latest, 10000):
            print(f"{height}/{latest}")
            # users who receive the receipt of depositing either via proxy-bridge or direct interaction
            addresses.update(
                i.args["to"]
                for i in token.events.Transfer().getLogs(
                    fromBlock=height,
                    toBlock=height + 10000 if height + 10000 < latest else latest,
                )
                if i.args["from"] == ZERO_ADDRESS or i.args["from"] == badger_tree
            )

        # remove from the addresses ----> DAO's msigs
        dao_msigs_to_remove = [
            dev_multi,
            badger_tree,
            techops,
            treasury_ops,
            ibbtc_multisig,
        ]
        for addr in dao_msigs_to_remove:
            addresses.remove(addr)

        sett_name = namings[idx]
        addresses_dict[sett_name] = sorted(addresses)
        print(f"naming: {namings[idx]}")
        print(f"\nFound {len(addresses)} addresses")

    return addresses_dict, latest


# encapsules for each address the total wbtc they are contributing into the products
def get_receipt_balances(addresses, block):

    """only run if contract are not recognise ->for asset in curve_swaps:
    Contract.from_explorer(asset)"""

    balances_setts = {}
    for idx, name in enumerate(namings):
        sett_receipt = Contract(setts_entitled[idx])
        # will be req to multiply the balanceOf to translate to underlying deposited
        mc_data = [
            [str(sett_receipt), sett_receipt.balanceOf.encode_input(addr)]
            for addr in addresses.get(name)
        ]
        multicall = Contract("0x5e227AD1969Ea493B43F840cfF78d08a6fc17796")

        balances = {}
        step = 30
        for i in range(0, len(mc_data), step):
            print(f"{i}/{len(mc_data)}")
            response = multicall.aggregate.call(
                mc_data[i : i + step], block_identifier=block
            )[1]
            try:
                decoded = [
                    sett_receipt.balanceOf.decode_output(data) for data in response
                ]
            except:
                # some setts may not exist, nothing to decode at that time
                continue

            decoded = [value for value in decoded]

            balances.update(
                {
                    addr.lower(): balance
                    for addr, balance in zip(addresses.get(name)[i : i + step], decoded)
                    if balance > 0
                }
            )

        balances_setts[name] = balances

    # prior to return, sum all of the common keys to generate an unique dict with each addresss contribution
    temp_input = [list(balances_setts[key].items()) for key in balances_setts]
    output = defaultdict(int)
    for d in temp_input:
        for item in d:
            output[item[0]] += item[1]

    return dict(output)


def get_proof(balances, snapshot_block, date):
    # use data/Convex_EPS/aidrop/eps files directly
    target_json = f"data/Convex_EPS/airdrop/eps/{date}/drop_proofs.json"
    with open(target_json) as f:
        msig_args_details = json.load(f)["users"][dev_multi_bsc_latest]
        # calc the distribution
        total_to_distribute = int(msig_args_details["amount"])
        total_contributed = sum(balances.values())

        balances = {
            k: int(Fraction(v * total_to_distribute, total_contributed))
            for k, v in balances.items()
        }
        balances = {k: v for k, v in balances.items() if v}

        addresses = deque(balances)
        while sum(balances.values()) < total_to_distribute:
            balances[addresses[0]] += 1
            addresses.rotate()

        # check what is going to be distribute is equal to what was claimed
        assert sum(balances.values()) == total_to_distribute

        elements = [
            (index, account, balances[account])
            for index, account in enumerate(sorted(balances))
        ]

        distribution = {
            "tokenTotal": hex(sum(balances.values())),
            "blockHeight": snapshot_block,
            "claims": {
                user: {"index": index, "amount": hex(amount)}
                for index, user, amount in elements
            },
        }

        return distribution, balances


def get_block_at_timestamp(timestamp):
    current = chain[-1]

    high = current.number - (current.timestamp - timestamp) // 15
    low = current.number - (current.timestamp - timestamp) // 11

    while low <= high:
        middle = low + (high - low) // 2
        block = chain[middle]
        if block.timestamp >= timestamp and chain[middle - 1].timestamp < timestamp:
            return middle
        elif block.timestamp < timestamp:
            low = middle + 1
        else:
            high = middle - 1
    raise ValueError


def takeSecond(elem):
    return elem[1]


def main():
    addresses_json = Path("scripts/snapshot/EPS/addresses.json")
    if addresses_json.exists():
        with addresses_json.open() as fp:
            data = json.load(fp)
            start_block = data["latest"]
            addresses = data["addresses"]
    else:
        start_block = 11380872
        addresses, height = get_depositors_sett(start_block)
        with addresses_json.open("w") as file:
            json.dump({"addresses": addresses, "latest": height}, file, indent=4)

    for date in last_weeks:
        dt = datetime.datetime.strptime(f"{date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=timezone.utc)
        snapshot_time = int(dt.timestamp())
        snapshot_block = get_block_at_timestamp(snapshot_time)
        date = dt.strftime("%Y-%m-%d")
        balances = get_receipt_balances(addresses, snapshot_block)
        # specify last arg -> X weeks back time, last week claims by default
        distribution, balances = get_proof(
            balances, snapshot_block, date.replace("-", "_")
        )
        os.makedirs("scripts/snapshot/EPS/distributions/", exist_ok=True)
        distro_json = Path(
            f"scripts/snapshot/EPS/distributions/distribution-{date}.json"
        )
        with distro_json.open("w") as fp:
            json.dump(distribution, fp, indent=4)

        # generate csv
        r = list(balances.items())
        for idx in range(len(r)):
            # format amount - better visual
            r[idx] = (r[idx][0], r[idx][1] / (10**18))

        r.sort(key=takeSecond, reverse=True)
        array_formatted_distribution = np.array(r)

        os.makedirs("scripts/snapshot/EPS/distributions_csv/", exist_ok=True)
        csv_file = open(
            f"scripts/snapshot/EPS/distributions_csv/distribution-{date}.csv",
            "w",
            newline="",
        )
        with csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["address", "amount"])
            writer.writeheader()
            write = csv.writer(csv_file)
            write.writerows(array_formatted_distribution)

        print(f"Created json & csv distributions for {date}")
