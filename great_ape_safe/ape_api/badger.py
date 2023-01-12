import json
import os
import requests
from decimal import Decimal

import pandas as pd
from brownie import chain, interface, ZERO_ADDRESS
from eth_abi import encode_abi

from helpers.addresses import r
from rich.console import Console


C = Console()


class Badger:
    """
    collection of all contracts and methods needed to interact with the badger
    system.
    """

    def __init__(self, safe):
        self.safe = safe

        # tokens
        self.badger = self.safe.contract(r.treasury_tokens.BADGER, interface.IBadger)

        # contracts
        self.tree = self.safe.contract(
            r.badger_wallets.badgertree, interface.IBadgerTreeV2
        )
        self.strat_bvecvx = self.safe.contract(
            r.strategies["native.vestedCVX"], interface.IVestedCvx
        )
        self.strat_graviaura = self.safe.contract(
            r.strategies["native.graviAURA"], interface.IVestedAura
        )
        self.timelock = self.safe.contract(
            r.governance_timelock, interface.IGovernanceTimelock
        )
        self.cvx_bribes_processor = self.safe.contract(
            r.cvx_bribes_processor, interface.IBribesProcessor
        )
        self.registry = self.safe.contract(r.registry, interface.IBadgerRegistry)
        self.registry_v2 = self.safe.contract(
            r.registry_v2, interface.IBadgerRegistryV2
        )
        self.station = self.safe.contract(r.badger_wallets.gas_station)
        self.rewards = self.safe.contract(r.hidden_hand.rewards_distributor)

        # misc
        self.api_url = "https://api.badger.com/v2/"
        self.api_hh_url = f"https://hhand.xyz/reward/{chain.id}/"

    def claim_all(self, json_file_path=None):
        """
        note: badger tree checks if `cycle` passed is equal to latest cycle,
        if not it will revert. therefore call is very time-sensitive!
        """

        if not json_file_path:
            url = self.api_url + "reward/tree/" + self.safe.address

            # grab args from api endpoint
            response = requests.get(url)
            json_data = response.json()
        else:
            file = open(json_file_path)
            json_data = json.load(file)["claims"][self.safe.address]

        if "message" in json_data.keys():
            if (
                json_data["message"]
                == f"{self.safe.address} does not have claimable rewards."
            ):
                return

        amounts_claimable = self.tree.getClaimableFor(
            self.safe.address,
            json_data["tokens"],
            json_data["cumulativeAmounts"],
        )[1]

        self.tree.claim(
            json_data["tokens"],
            json_data["cumulativeAmounts"],
            json_data["index"],
            json_data["cycle"],
            json_data["proof"],
            amounts_claimable,
        )

    def claim_bribes_votium(self):
        """
        accepts a dict with `keys` being equal to the directory names used in
        the official votium repo (https://github.com/oo-00/Votium) and its
        `values` being the respective token's address.
        """
        merkle_stash = self.safe.contract(
            r.votium.multiMerkleStash, interface.IMultiMerkleStash
        )
        aggregate = {"tokens": [], "indexes": [], "amounts": [], "proofs": []}

        with open("data/Votium/merkle/activeTokens.json") as fp:
            active_tokens = json.load(fp)
        for token in active_tokens:
            directory = "data/Votium/merkle/"
            try:
                last_json = sorted(os.listdir(directory + token["symbol"]))[-1]
            except FileNotFoundError:
                # given token is not a votium reward
                continue
            with open(directory + token["symbol"] + f"/{last_json}") as f:
                try:
                    leaf = json.load(f)["claims"][self.strat_bvecvx.address]
                except KeyError:
                    # no claimables for the strat for this particular token
                    continue
                if not merkle_stash.isClaimed(token["value"], leaf["index"]):
                    aggregate["tokens"].append(token["value"])
                    aggregate["indexes"].append(leaf["index"])
                    aggregate["amounts"].append(int(leaf["amount"], 0))
                    aggregate["proofs"].append(leaf["proof"])
        if len(aggregate["tokens"]) > 0:
            self.strat_bvecvx.claimBribesFromVotium(
                r.votium.multiMerkleStash,
                self.strat_bvecvx.address,
                aggregate["tokens"],
                aggregate["indexes"],
                aggregate["amounts"],
                aggregate["proofs"],
            )
        return dict(zip(aggregate["tokens"], aggregate["amounts"]))

    def claim_bribes_convex(self, eligible_claims):
        """
        loop over `eligible_claims` dict to confirm if there are claimable
        rewards, and pass a list of claimable rewards to the strat to claim
        in one bulk tx.
        """
        self.safe.init_convex()
        claimables = []
        for token_addr in eligible_claims:
            claimable = self.safe.convex.cvx_extra_rewards.claimableRewards(
                self.strat_bvecvx.address, token_addr
            )
            if claimable > 0:
                claimables.append(token_addr)
        if len(claimables) > 0:
            self.strat_bvecvx.claimBribesFromConvex(claimables)

    def get_hh_data(self, address=None):
        """
        get hidden hand data for a particular address
        """
        address = address if address else self.safe.address
        url = self.api_hh_url + address
        r = requests.get(url)
        if not r.ok:
            r.raise_for_status()
        return r.json()["data"]

    def claim_bribes_hidden_hands(self, claim_from_strat=True) -> dict:
        """
        grabs the available claimable tokens from HH endpoint,
        loop it thru them and returning the list of addresses
        and mantissas for latter processing.
        """
        address = (
            self.strat_graviaura.address if claim_from_strat else self.safe.address
        )
        data = self.get_hh_data(address)

        def transform_claimable(amount_string, n_decimals):
            # if the last number is a zero it gets omitted by the api,
            # here we pad the matissa with zeroes to correct for this
            assert "." in amount_string
            splitted = amount_string.split(".")
            return splitted[0] + splitted[-1].ljust(n_decimals, "0")

        aggregate = {"tokens": [], "amounts": []}
        for item in data:
            aggregate["tokens"].append(item["token"])
            aggregate["amounts"].append(
                transform_claimable(item["claimable"], item["decimals"])
            )

        metadata = [
            (
                item["claimMetadata"]["identifier"],
                item["claimMetadata"]["account"],
                item["claimMetadata"]["amount"],
                item["claimMetadata"]["merkleProof"],
            )
            for item in data
        ]

        if claim_from_strat:
            self.strat_graviaura.claimBribesFromHiddenHand(
                self.rewards.address,
                metadata,
            )
        else:
            self.rewards.claim(metadata)

        return dict(zip(aggregate["tokens"], aggregate["amounts"]))

    def sweep_reward_token(self, token_addr):
        """
        Sweeps reward token from the vestedCVX strategy into
        the BribesProcessor.
        """
        reward = interface.ERC20(token_addr)
        prev_strategy_balance = reward.balanceOf(self.strat_bvecvx.address)
        # Ensure that there are tokens to sweep
        if prev_strategy_balance == 0:
            C.print(f"[red]There are no rewards to sweep for: {reward.symbol()}[/red]")
            return 0
        prev_bribes_processor_balance = reward.balanceOf(
            self.cvx_bribes_processor.address
        )

        # Sweep the reward token
        self.strat_bvecvx.sweepRewardToken(token_addr)

        assert (
            reward.balanceOf(self.cvx_bribes_processor.address)
            - prev_bribes_processor_balance
        ) == prev_strategy_balance
        assert reward.balanceOf(self.strat_bvecvx.address) == 0

        return prev_strategy_balance

    def queue_timelock(self, target_addr, signature, data, dump_dir, delay_in_days=2.3):
        """
        Queue a call to `target_addr` with `signature` containing `data` into the
        'timelock' contract. Delay is slightly over 48 hours by default.
        Example of `signature` and `data`:
        signature = 'approveStrategy(address,address)'
        data = eth_abi.encode_abi(
            ['address', 'address'],
            [addr_var1, addr_var2],
        )
        """

        # calc timestamp of execution
        delay = int(delay_in_days * 60 * 60 * 24)
        eta = chain.time() + delay

        # queue actual action to the timelock
        tx = self.timelock.queueTransaction(target_addr, 0, signature, data, eta)

        # dump tx details to json file
        filename = tx.events["QueueTransaction"]["txHash"]
        C.print(f"Dump Directory: {dump_dir}")
        os.makedirs(dump_dir, exist_ok=True)
        with open(f"{dump_dir}{filename}.json", "w") as f:
            tx_data = {
                "target": target_addr,
                "eth": 0,
                "signature": signature,
                "data": data.hex(),
                "eta": eta,
            }
            json.dump(tx_data, f, indent=4, sort_keys=True)

    def execute_timelock(self, queueTx_dir):
        """
        Loops through all the JSON files within the given 'queueTx_dir' and executes
        the txs that have already been queued on the 'timelock'.
        """
        path = os.path.dirname(queueTx_dir)
        directory = os.fsencode(path)

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if not filename.endswith(".json"):
                continue
            txHash = filename.replace(".json", "")

            if self.timelock.queuedTransactions(txHash) == True:
                with open(f"{queueTx_dir}{filename}") as f:
                    tx = json.load(f)

                C.print(f"[green]Executing tx with parameters:[/green] {tx}")

                self.timelock.executeTransaction(
                    tx["target"], 0, tx["signature"], tx["data"], tx["eta"]
                )
            else:
                with open(f"{queueTx_dir}{filename}") as f:
                    tx = json.load(f)
                C.print(f"[red]Tx not yet queued:[/red] {tx}")

    def whitelist(self, candidate_addr, sett_addr):
        sett = interface.ISettV4h(sett_addr, owner=self.safe.account)
        if not sett.approved(candidate_addr):
            governor = sett.governance()
            if governor == self.safe.address:
                C.print(f"whitelisting {candidate_addr} on {sett_addr}...")
                sett.approveContractAccess(candidate_addr)
                assert sett.approved(candidate_addr)
                return True
            elif hasattr(sett, "strategist"):
                if sett.strategist() == self.safe.address:
                    C.print(f"whitelisting {candidate_addr} on {sett_addr}...")
                    sett.approveContractAccess(candidate_addr)
                    assert sett.approved(candidate_addr)
                    return True
            elif governor == self.timelock.address:
                C.print(
                    f"whitelisting {candidate_addr} on {sett_addr} through timelock..."
                )
                self.queue_timelock(
                    target_addr=sett.address,
                    signature="approveContractAccess(address)",
                    data=encode_abi(["address"], [candidate_addr]),
                    dump_dir=f"data/badger/timelock/whitelister/",
                    delay_in_days=4.3,
                )
                return True
            else:
                C.print(
                    f"cannot whitelist on {sett_addr}: no governance\n",
                    style="dark_orange",
                )
                return False

    def wire_up_controller(self, controller_addr, vault_addr, strat_addr):
        controller = interface.IController(controller_addr, owner=self.safe.account)
        vault = interface.ISettV4h(vault_addr, owner=self.safe.account)
        strategy = interface.IStrategy(strat_addr, owner=self.safe.account)
        want = vault.token()

        assert want == strategy.want()
        C.print(f"[green]Same want for vault and strategy: {want}[/green]\n")

        C.print(f"Wiring vault: {vault_addr}, on controller: {controller_addr}...")
        controller.setVault(want, vault_addr)
        assert controller.vaults(want) == vault_addr

        C.print(f"Wiring strategy: {strat_addr}, on controller: {controller_addr}...")
        controller.approveStrategy(want, strat_addr)
        controller.setStrategy(want, strat_addr)
        assert controller.strategies(want) == strat_addr

    def promote_vault(self, vault_addr, vault_version, vault_metadata, vault_status):
        self.registry_v2.promote(
            vault_addr, vault_version, vault_metadata, vault_status
        )
        C.print(f"Promote: {vault_addr} ({vault_version}) to {vault_status}")

    def demote_vault(self, vault_addr, vault_status):
        self.registry_v2.demote(vault_addr, vault_status)
        C.print(f"Demote: {vault_addr} to {vault_status}")

    def update_metadata(self, vault_addr, vault_metadata):
        self.registry_v2.updateMetadata(vault_addr, vault_metadata)
        C.print(f"Update Metadata: {vault_addr} to {vault_metadata}")

    def set_key_on_registry(self, key, target_addr):
        # Ensures key doesn't currently exist
        assert self.registry_v2.get(key) == ZERO_ADDRESS

        self.registry_v2.set(key, target_addr)

        assert self.registry_v2.get(key) == target_addr
        C.print(f"{key} was added to the registry at {target_addr}")

    def migrate_key_on_registry(self, key):
        value = self.registry.get(key)
        assert value != ZERO_ADDRESS
        self.set_key_on_registry(key, value)

    def from_gdigg_to_digg(self, gdigg):
        digg = interface.IUFragments(r.treasury_tokens.DIGG, owner=self.safe.account)
        return Decimal(
            gdigg * digg._initialSharesPerFragment() / digg._sharesPerFragment()
        )

    def get_order_for_processor(
        self,
        bribes_processor,
        sell_token,
        mantissa_sell,
        buy_token,
        mantissa_buy=None,
        deadline=60 * 60,
        coef=1,
        prod=False,
    ):
        if not hasattr(self.safe, "cow"):
            self.safe.init_cow(prod=prod)
        order_payload, order_uid = self.safe.cow._sell(
            sell_token,
            mantissa_sell,
            buy_token,
            mantissa_buy,
            deadline,
            coef,
            destination=bribes_processor.address,
            origin=bribes_processor.address,
        )
        order_payload["kind"] = str(bribes_processor.KIND_SELL())
        order_payload["sellTokenBalance"] = str(bribes_processor.BALANCE_ERC20())
        order_payload["buyTokenBalance"] = str(bribes_processor.BALANCE_ERC20())
        order_payload.pop("signingScheme")
        order_payload.pop("signature")
        order_payload.pop("from")
        order_payload = tuple(order_payload.values())

        assert bribes_processor.getOrderID(order_payload) == order_uid

        return order_payload, order_uid

    def set_gas_station_watchlist(self):
        labels, addrs, min_bals, min_top_ups = [], [], [], []
        for label, addr in r.badger_wallets.items():
            min_bal = 2e18
            min_top_up = 0.5e18
            if not label.startswith("ops_") or "multisig" in label:
                continue
            if "executor" in label:
                min_bal = 1e18
            if label == "ops_botsquad":
                min_bal = 5e18
            if label == "ops_deployer":
                min_bal = 5e18
            labels.append(label)
            addrs.append(addr)
            min_bals.append(min_bal)
            min_top_ups.append(min_top_up)
        print(
            pd.DataFrame(
                {"addrs": addrs, "min_bals": min_bals, "min_top_ups": min_top_ups},
                index=labels,
            )
        )
        self.station.setWatchList(addrs, min_bals, min_top_ups)

    def set_guestlist_user_cap(self, guestlist, cap):
        guestlist = interface.IVipCappedGuestListBbtcUpgradeable(
            guestlist, owner=self.safe.account
        )
        guestlist.setUserDepositCap(cap)
        assert guestlist.userDepositCap() == cap
        C.print(f"[green]New user cap: {cap}[/green]")

    def set_guestlist_total_cap(self, guestlist, cap):
        guestlist = interface.IVipCappedGuestListBbtcUpgradeable(
            guestlist, owner=self.safe.account
        )
        guestlist.setTotalDepositCap(cap)
        assert guestlist.totalDepositCap() == cap
        C.print(f"[green]New total cap: {cap}[/green]")
