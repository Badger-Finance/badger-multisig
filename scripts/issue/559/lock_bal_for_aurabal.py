from brownie import Contract

from great_ape_safe import GreatApeSafe
from helpers.addresses import r


def main():
    '''
    ref: https://github.com/aurafinance/aura-contracts-lite
    ref: https://dev.balancer.fi/references/error-codes
    ref: https://docs.aura.finance/developers/deployed-addresses
    kovan: https://whimsical-snowman-458.notion.site/Deployment-a5dc796b4923412c89b57d06de51141b
    '''
    voter = GreatApeSafe(r.badger_wallets.bvecvx_voting_multisig)
    bal = voter.contract(r.treasury_tokens.BAL)

    wrapper = voter.contract(r.aura.wrapper)
    aura = voter.contract(r.treasury_tokens.AURA)
    aurabal = voter.contract(r.treasury_tokens.AURABAL)

    voter.init_balancer()
    voter.take_snapshot([bal, aura, aurabal])

    bal.approve(wrapper, bal.balanceOf(voter))
    wrapper.deposit(
        bal.balanceOf(voter),  # uint256 _amount
        wrapper.getMinOut(bal.balanceOf(voter), 9950),  # uint256 _minOut
        True,  # bool _lock
        r.aura.aurabal_staking  # address _stakeAddress
    )

    print(Contract(r.aura.aurabal_staking).balanceOf(voter))

    voter.post_safe_tx()
