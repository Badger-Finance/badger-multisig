import os
import requests
from decimal import Decimal, InvalidOperation

from brownie import web3, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r
from pycoingecko import CoinGeckoAPI

SNAPSHOT_URL = "https://hub.snapshot.org/graphql?"

# queries for choices and proposals info
QUERY_PROPOSAL_INFO = """
query ($proposal_id: String) {
  proposal(id: $proposal_id) {
    choices
  }
}
"""

# `state: "all"` ensures all proposals are included
QUERY_PROPOSALS = """
query {
  proposals(first: 100, where: { space: "gauges.aurafinance.eth" , state: "all"}) {
    id
  }
}
"""

# gauge to bribe in aura
AURA_TARGET = "80/20 BADGER/WBTC"
AURA_TARGET = "50/50 BADGER/rETH"

# gauge to bribe in convex
CONVEX_TARGET = "BADGER+FRAXBP (0x13B8…)"

# snapshot differentiator after moving into `gauges.aurafinance.eth` space
AURA_SNAP_DIFF_FACTOR = 1000000

MAX_BPS = 10_000


def get_index(proposal_id, target):
    # grab data from the snapshot endpoint re proposal choices
    response = requests.post(
        SNAPSHOT_URL,
        json={
            "query": QUERY_PROPOSAL_INFO,
            "variables": {"proposal_id": proposal_id},
        },
    )
    choices = response.json()["data"]["proposal"]["choices"]
    choice = choices.index(target)
    return choice


def main(
    badger_bribe_in_aura=0,
    badger_bribe_in_balancer=0,
    badger_bribe_in_votium=0,
    badger_bribe_in_frax=0,
    badger_bribe_in_bunni=0,  # NOTE: dollar denominated. Badger calculation is done internaly
    max_tokens_per_vote=0,  # Maximum amount of incentives to be used per round (Hidden Hands V2)
    periods=1,  # Rounds to be covered by the incentives deposited (Hidden Hands V2)
    badger_bribe_in_liquis=0,  # NOTE: dollar denominated. Badger calculation is done internaly, the incentive gets process via Paladin
    duration_paladin_quest=1,  # Duration (in number of periods) of the Quest
    reward_per_vote_liquis=0,  # Amount of reward per vlLIQ
    aura_proposal_id=None,
    convex_proposal_id=None,
):
    bribes = {
        "aura": badger_bribe_in_aura,
        "balancer": badger_bribe_in_balancer,
        "votium": badger_bribe_in_votium,
        "frax": badger_bribe_in_frax,
        "bunni": badger_bribe_in_bunni,
        "liquis": badger_bribe_in_liquis,
    }
    for k, v in bribes.items():
        try:
            bribes[k] = Decimal(v)
        except InvalidOperation:
            pass

    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    badger = safe.contract(r.treasury_tokens.BADGER)

    safe.take_snapshot([badger])

    bribe_vault = safe.contract(r.hidden_hand.bribe_vault, interface.IBribeVault)
    aura_briber = safe.contract(r.hidden_hand.aura_briber, interface.IBribeMarket)
    balancer_briber = safe.contract(
        r.hidden_hand.balancer_briber, interface.IBribeMarket
    )
    votium_briber = safe.contract(r.votium.bribe, interface.IVotiumBribe)
    frax_briber = safe.contract(r.hidden_hand.frax_briber, interface.IBribeMarket)
    bunni_briber = safe.contract(r.hidden_hand.bunni_briber, interface.IBribeMarket)

    palading_quest_board_veliq = safe.contract(
        r.paladin.quest_board_veliq, interface.IQuestBoard
    )

    if bribes["aura"] > 0:
        assert aura_proposal_id
        choice = get_index(aura_proposal_id, AURA_TARGET)

        # grab data from proposals to find out the proposal index
        response = requests.post(SNAPSHOT_URL, json={"query": QUERY_PROPOSALS})
        # reverse the order to have from oldest to newest
        proposals = response.json()["data"]["proposals"][::-1]
        for proposal in proposals:
            if aura_proposal_id == proposal["id"]:
                proposal_index = proposals.index(proposal) + AURA_SNAP_DIFF_FACTOR
                break
        prop = web3.solidityKeccak(["uint256", "uint256"], [proposal_index, choice])

        # NOTE: debugging prints to verify
        print("Current total proposal in aura snap: ", len(proposals))
        print("Proposal index:", proposal_index)
        print("Choice:", choice)
        print("Proposal hash:", prop.hex())

        mantissa = int(bribes["aura"] * Decimal(1e18))

        badger.approve(bribe_vault, mantissa)
        aura_briber.depositBribe(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
            max_tokens_per_vote,  # uint256 _maxTokensPerVote,
            periods,  #  uint256 _periods
        )

    def bribe_balancer(gauge, mantissa):
        prop = web3.solidityKeccak(["address"], [gauge])
        mantissa = int(mantissa)

        badger.approve(bribe_vault, mantissa)
        print(gauge, prop.hex(), mantissa)
        balancer_briber.depositBribe(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
            max_tokens_per_vote,  # uint256 _maxTokensPerVote,
            periods,  #  uint256 _periods
        )

    if isinstance(bribes["balancer"], str):
        # this allows for passing `main 0 12000,4000` for example to the script
        # in order to bribe both markets at the same time
        bribes_split = bribes["balancer"].split(",")
        if Decimal(bribes_split[0]) > 0:
            bribe_balancer(
                r.balancer.B_20_BTC_80_BADGER_GAUGE,
                Decimal(bribes_split[0]) * Decimal(1e18),
            )
        if Decimal(bribes_split[1]) > 0:
            bribe_balancer(
                r.balancer.B_50_BADGER_50_RETH_GAUGE,
                Decimal(bribes_split[1]) * Decimal(1e18),
            )
    elif bribes["balancer"] > 0:
        bribe_balancer(
            r.balancer.B_50_BADGER_50_RETH_GAUGE, bribes["balancer"] * Decimal(1e18)
        )

    if bribes["votium"] > 0:
        assert convex_proposal_id
        # https://etherscan.io/address/0x19bbc3463dd8d07f55438014b021fb457ebd4595#code#F7#L30
        prop = web3.keccak(hexstr=convex_proposal_id)
        mantissa = int(bribes["votium"] * Decimal(1e18))
        choice = get_index(convex_proposal_id, CONVEX_TARGET)

        badger.approve(votium_briber, mantissa)
        votium_briber.depositBribe(badger, mantissa, prop, choice)

    if bribes["frax"] > 0:
        prop = web3.solidityKeccak(["address"], [r.frax.BADGER_FRAXBP_GAUGE])
        mantissa = int(bribes["frax"] * Decimal(1e18))

        badger.approve(bribe_vault, mantissa)
        frax_briber.depositBribe(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
            max_tokens_per_vote,  # uint256 _maxTokensPerVote,
            periods,  #  uint256 _periods
        )

    if bribes["bunni"] > 0:
        # NOTE: Treasury decision is expressed in dollars
        cg = CoinGeckoAPI(os.getenv("COINGECKO_API_KEY"))
        badger_rate = Decimal(
            cg.get_price(ids="badger-dao", vs_currencies="usd")["badger-dao"]["usd"]
        )

        prop = web3.solidityKeccak(
            ["address"], [r.bunni.badger_wbtc_bunni_gauge_309720_332580]
        )
        print("prop", prop.hex())
        mantissa = int(bribes["bunni"] / badger_rate * Decimal(1e18))

        badger.approve(bribe_vault, mantissa)
        bunni_briber.depositBribe(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
            max_tokens_per_vote,  # uint256 _maxTokensPerVote,
            periods,  #  uint256 _periods
        )

    if bribes["liquis"] > 0:
        # NOTE: Treasury decision is expressed in dollars
        # ref: https://forum.badger.finance/t/34-liquis-partner-engagement/6029
        cg = CoinGeckoAPI(os.getenv("COINGECKO_API_KEY"))
        badger_rate = Decimal(
            cg.get_price(ids="badger-dao", vs_currencies="usd")["badger-dao"]["usd"]
        )

        mantissa = int(bribes["liquis"] / badger_rate * Decimal(1e18))

        platform_fee = int((Decimal(mantissa) * palading_quest_board_veliq.platformFee()) / MAX_BPS)

        min_reward_per_vote = palading_quest_board_veliq.minRewardPerVotePerToken(
            badger
        )

        reward_per_vote_liquis = reward_per_vote_liquis * 1e18
        objective = (Decimal(mantissa) * Decimal(1e18)) / Decimal(reward_per_vote_liquis)

        assert reward_per_vote_liquis > min_reward_per_vote
        assert objective > palading_quest_board_veliq.minObjective()
        assert duration_paladin_quest >= 1

        badger.approve(palading_quest_board_veliq, mantissa + platform_fee)
        palading_quest_board_veliq.createQuest(
            r.bunni.badger_wbtc_bunni_gauge_309720_332580,  # address gauge
            badger.address,  # address rewardToken
            duration_paladin_quest,  # uint48 duration
            objective,  # uint256 objective
            reward_per_vote_liquis,  # uint256 rewardPerVote
            mantissa,  # uint256 totalRewardAmount
            platform_fee,  # uint256 feeAmount
        )

    safe.post_safe_tx()
