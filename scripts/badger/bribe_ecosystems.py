import requests
from decimal import Decimal

from brownie import web3, interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

url = "https://hub.snapshot.org/graphql?"

# QUERIES FOR CHOICES AND PROPOSALS INFO
query_proposal_info = """
query ($proposal_id: String) {
  proposal(id: $proposal_id) {
    choices
  }
}
"""
# NOTE: add more states to ensure all proposals are included
query_proposals = """
query {
  proposals(first: 100, where: { space: "aurafinance.eth" , state: "all"}) {
    id
  }
}
"""

# gauge to bribe in aura
GAUGE_TARGET = "80/20 BADGER/WBTC"

# gauge to bribe in convex
CONVEX_TARGET = "BADGER+crvFRAX (0x13B8…)"


def get_index(proposal_id, target):
    # grab data from the snap endpoint re proposal choices
    response = requests.post(
        url,
        json={
            "query": query_proposal_info,
            "variables": {"proposal_id": proposal_id},
        },
    )
    choices = response.json()["data"]["proposal"]["choices"]
    choice = choices.index(target)
    return choice

# NOTE: leaving as default the breakdown vote by council temporalily
def main(
    badger_bribe_in_aura=8000,
    badger_bribe_in_balancer=0,
    badger_bribe_in_votium=8000,
    aura_proposal_id="0xcd2c48e7a2dc7b5ea333447c4b0b9a0e312329ddbec4cedc64b606e9b0ed6feb",
    convex_proposal_id="0xee37337fd2b8b5112ac4efd2948d58e4e44f59ee904c70650d26ece60276ed9f",
):
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    badger_bribe_in_aura = int(badger_bribe_in_aura)
    badger_bribe_in_balancer = int(badger_bribe_in_balancer)
    badger_bribe_in_convex = int(badger_bribe_in_votium)

    badger = interface.ERC20(r.treasury_tokens.BADGER, owner=safe.account)

    safe.take_snapshot([badger])

    bribe_vault = interface.IBribeVault(r.hidden_hand.bribe_vault, owner=safe.account)

    balancer_briber = interface.ITokenmakBribe(
        r.hidden_hand.balancer_briber, owner=safe.account
    )

    aura_briber = interface.IAuraBribe(r.hidden_hand.aura_briber, owner=safe.account)

    votium_bribe = safe.contract(r.votium.bribe)

    if badger_bribe_in_aura > 0:
        choice = get_index(aura_proposal_id, GAUGE_TARGET)

        # grab data from proposals to find out the proposal index
        response = requests.post(
            url,
            json={"query": query_proposals},
        )
        # reverse the order to have from oldest to newest
        proposals = response.json()["data"]["proposals"][::-1]
        for proposal in proposals:
            if aura_proposal_id == proposal["id"]:
                proposal_index = proposals.index(proposal)
                break
        prop = web3.solidityKeccak(["uint256", "uint256"], [proposal_index, choice])

        # NOTE: debugging prints to verify
        print("Current total proposal in aura snap: ", len(proposals))
        print("Proposal index:", proposal_index)
        print("Choice:", choice)
        print("Proposal hash: ",prop.hex())

        mantissa = int(Decimal(badger_bribe_in_aura) * Decimal(1e18))

        badger.approve(bribe_vault, mantissa)
        aura_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
        )

    if badger_bribe_in_balancer > 0:
        prop = web3.solidityKeccak(["address"], [r.balancer.B_20_BTC_80_BADGER_GAUGE])

        mantissa = int(
            Decimal(badger_bribe_in_balancer) * Decimal(1e18)
        )

        badger.approve(bribe_vault, mantissa)
        balancer_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
        )

    if badger_bribe_in_convex > 0:
        # https://etherscan.io/address/0x19bbc3463dd8d07f55438014b021fb457ebd4595#code#F7#L30
        proposal = web3.keccak(hexstr=convex_proposal_id)
        mantissa = int(
            Decimal(badger_bribe_in_convex) * Decimal(1e18)
        )
        choice = get_index(convex_proposal_id, CONVEX_TARGET)

        badger.approve(votium_bribe, mantissa)
        votium_bribe.depositBribe(badger, mantissa, proposal, choice)

    safe.post_safe_tx()
