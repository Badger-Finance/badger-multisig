from datetime import datetime, timezone
import requests
import pandas as pd
from rich.console import Console
from rich.pretty import pprint

from brownie import Contract, web3
from helpers.addresses import r

console = Console()

# NOTE: request info and fill it up over time depending on rotations
replacements = {
    "techops_multisig": {
        "0x10C7a2ca16116E5C998Bfa3BC9CEF464475B18ff": "0x0a9af7FAba0d5DF7A8C881e1B9cd679ee07Af8A2",
        "0xeE8b29AA52dD5fF2559da2C50b1887ADee257556": "0xfA5bb45895Cb3C0aE5B1583Fe068f009A48F0187",
        "0xBB2281cA5B4d07263112604D1F182AD0Ab26a252": "0xE8eA1D8B3a5A4CEC7E94AE330fF18E82B5D22fA6",
    }
}

# we introduce times of judgement as args (default: Q2)
# likely worth running once at the end of each quarter
def main(start_time=1648771200, end_time=1656547200):
    msigs = r.badger_wallets

    console.print(
        f"Time interval inspected: [{datetime.fromtimestamp(start_time, tz=timezone.utc)}, {datetime.fromtimestamp(end_time, tz=timezone.utc)}]"
    )

    for key, addr in msigs.items():
        if "multisig" in key:
            console.print(f"[green] Inspecting {key} at {addr}[/green]")

            safe = Contract(addr)

            total_tx = 0

            # judging signed amount
            owners_signed = dict.fromkeys(safe.getOwners(), 0)

            url = f"https://safe-transaction.gnosis.io/api/v1/safes/{web3.toChecksumAddress(addr)}/transactions/"
            urls = [url]

            for next_url in urls:
                while next_url:
                    response = requests.get(next_url)
                    data = response.json()
                    next_url = data["next"]
                    for tx in data["results"]:
                        # posting time
                        submission_date_ts = pd.to_datetime(
                            tx["submissionDate"]
                        ).timestamp()

                        if (
                            submission_date_ts >= start_time
                            and submission_date_ts <= end_time
                        ):
                            # only sum within interval time of judgement
                            total_tx += 1

                            # check confirmations
                            confirmations = tx["confirmations"]

                            for confirmation in confirmations:
                                owner = confirmation["owner"]
                                signing_tx_ts = pd.to_datetime(
                                    confirmation["submissionDate"]
                                ).timestamp()
                                # leaving here for next iteration of framework
                                reaction_ts = signing_tx_ts - submission_date_ts

                                if owner in owners_signed.keys():
                                    try:
                                        owners_signed[owner] += 1
                                    except KeyError:
                                        try:
                                            # likely key was replace with other owner
                                            owner = replacements[key][owner]
                                            owners_signed[owner] += 1
                                        except KeyError:
                                            continue

            owners_signed = {
                k: pct_activity(total_tx, signed)
                for k, signed in sort_descendecing(owners_signed).items()
            }

            console.print(f"Total txs: {total_tx}")

            # below 25% worth evaluating rotation
            pprint(owners_signed)


def pct_activity(total, signed):
    if total > 0:
        return "{:.2%}".format(signed / total)
    return "0.00%"


def sort_descendecing(d):
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=True))
