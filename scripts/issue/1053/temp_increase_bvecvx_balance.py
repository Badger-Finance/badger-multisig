from great_ape_safe import GreatApeSafe
from helpers.addresses import r


# note actual numbers changed from ticket's numbers due to recent auto unlock/divest:
# https://etherscan.io/tx/0x107910c7251dbb47e9b81aeb509c44d506383c8c502d9c8cb03872697dd4c15d

# actual numbers:
NEEDED = 69884615940476827071326
PENDING = 19234917575004743000000
# current: 32933749927336222016371
# deficit: needed - pending - current = 17715948438135862054955
# rounding up here to create a margin of error
DEFICIT = 20_000e18


def main():
    voter = GreatApeSafe(r.badger_wallets.treasury_voter_multisig)
    cvx = voter.contract(r.treasury_tokens.CVX)
    bvecvx = voter.contract(r.treasury_tokens.bveCVX)

    voter.take_snapshot([cvx, bvecvx])
    initial_cvx = cvx.balanceOf(voter)
    cvx.approve(bvecvx, DEFICIT)
    bvecvx.deposit(DEFICIT)
    assert bvecvx.balanceOf(voter) >= NEEDED - PENDING
    voter.post_safe_tx(gen_tenderly=False)

    voter.take_snapshot([cvx, bvecvx])
    bvecvx.withdraw(DEFICIT)
    assert cvx.balanceOf(voter) >= initial_cvx
    voter.post_safe_tx(gen_tenderly=False)
