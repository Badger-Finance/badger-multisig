import requests
from decimal import Decimal

from brownie import web3, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


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
  proposals(first: 100, where: { space: "aurafinance.eth" , state: "all"}) {
    id
  }
}
"""

# gauge to bribe in aura
AURA_TARGET = "80/20 BADGER/WBTC"  # or "50/50 BADGER/rETH"!

# gauge to bribe in convex
CONVEX_TARGET = "BADGER+crvFRAX (0x13B8…)"


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
    aura_proposal_id=None,
    convex_proposal_id=None,
):
    badger_bribe_in_aura = Decimal(badger_bribe_in_aura)
    badger_bribe_in_balancer = Decimal(badger_bribe_in_balancer)
    badger_bribe_in_convex = Decimal(badger_bribe_in_votium)
    badger_bribe_in_frax = Decimal(badger_bribe_in_frax)

    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    badger = safe.contract(r.treasury_tokens.BADGER)

    safe.take_snapshot([badger])

    bribe_vault = safe.contract(r.hidden_hand.bribe_vault, interface.IBribeVault)
    aura_briber = safe.contract(r.hidden_hand.aura_briber, interface.IAuraBribe)
    balancer_briber = safe.contract(
        r.hidden_hand.balancer_briber, interface.IBalancerBribe
    )
    votium_briber = safe.contract(r.votium.bribe, interface.IVotiumBribe)
    frax_briber = safe.contract(r.hidden_hand.frax_briber, interface.IFraxBribe)

    if badger_bribe_in_aura > 0:
        assert aura_proposal_id
        choice = get_index(aura_proposal_id, AURA_TARGET)

        # grab data from proposals to find out the proposal index
        response = requests.post(SNAPSHOT_URL, json={"query": QUERY_PROPOSALS})
        # reverse the order to have from oldest to newest
        proposals = response.json()["data"]["proposals"][::-1]
        for prop in proposals:
            if aura_proposal_id == prop["id"]:
                proposal_index = proposals.index(prop)
                break
        prop = web3.solidityKeccak(["uint256", "uint256"], [proposal_index, choice])

        # NOTE: debugging prints to verify
        print("Current total proposal in aura snap: ", len(proposals))
        print("Proposal index:", proposal_index)
        print("Choice:", choice)
        print("Proposal hash:", prop.hex())

        mantissa = int(badger_bribe_in_aura * Decimal(1e18))

        badger.approve(bribe_vault, mantissa)
        aura_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
        )

    if badger_bribe_in_balancer > 0:
        prop = web3.solidityKeccak(["address"], [r.balancer.B_20_BTC_80_BADGER_GAUGE])
        mantissa = int(badger_bribe_in_balancer * Decimal(1e18))

        badger.approve(bribe_vault, mantissa)
        balancer_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
        )

    if badger_bribe_in_convex > 0:
        assert convex_proposal_id
        # https://etherscan.io/address/0x19bbc3463dd8d07f55438014b021fb457ebd4595#code#F7#L30
        prop = web3.keccak(hexstr=convex_proposal_id)
        mantissa = int(badger_bribe_in_convex * Decimal(1e18))
        choice = get_index(convex_proposal_id, CONVEX_TARGET)

        badger.approve(votium_briber, mantissa)
        votium_briber.depositBribe(badger, mantissa, prop, choice)

    if badger_bribe_in_frax > 0:
        prop = web3.solidityKeccak(["address"], [r.frax.BADGER_FRAXBP_GAUGE])
        mantissa = int(badger_bribe_in_frax * Decimal(1e18))

        badger.approve(bribe_vault, mantissa)
        frax_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
        )

    safe.post_safe_tx()
