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
query_proposals = """
query {
  proposals(where: { space: "aurafinance.eth" }) {
    id
  }
}
"""

# gauge to bribe in aura
GAUGE_TARGET = "80/20 BADGER/WBTC"


def main(
    badger_bribe_in_aura=0,
    badger_bribe_in_balancer=0,
    aura_proposal_id="0x2445e521270db2ef0c3f6fae8903c5a753d48e112928507ca1d479a3b7b90bfd",
):
    safe = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)
    badger_bribe_in_aura = int(badger_bribe_in_aura)
    badger_bribe_in_balancer = int(badger_bribe_in_balancer)

    badger = interface.ERC20(r.treasury_tokens.BADGER, owner=safe.account)

    safe.take_snapshot([badger])

    bribe_vault = interface.IBribeVault(r.hidden_hand.bribe_vault, owner=safe.account)

    balancer_briber = interface.ITokenmakBribe(
        r.hidden_hand.balancer_briber, owner=safe.account
    )

    aura_briber = interface.IAuraBribe(r.hidden_hand.aura_briber, owner=safe.account)

    if badger_bribe_in_aura > 0:
        # grab data from the snap endpoint re proposal choices
        response = requests.post(
            url,
            json={
                "query": query_proposal_info,
                "variables": {"proposal_id": aura_proposal_id},
            },
        )
        choices = response.json()["data"]["proposal"]["choices"]
        choice = choices.index(GAUGE_TARGET)

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
        mantissa = int(Decimal(badger_bribe_in_aura) * Decimal(10 ** badger.decimals()))
        badger.approve(bribe_vault, mantissa)

        aura_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
        )

    if badger_bribe_in_balancer > 0:
        prop = web3.solidityKeccak(["address"], [r.balancer.B_20_BTC_80_BADGER_GAUGE])

        mantissa = int(
            Decimal(badger_bribe_in_balancer) * Decimal(10 ** badger.decimals())
        )
        badger.approve(bribe_vault, mantissa)

        balancer_briber.depositBribeERC20(
            prop,  # bytes32 proposal
            badger,  # address token
            mantissa,  # uint256 amount
        )

    safe.post_safe_tx()
