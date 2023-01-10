import pytest

PROPOSAL_SINGLE_CHOICE = (
    "0xdded9266cc2c671793d6ee9db2b6328222399e7314a265b5ff50f3381edf48fc"
)
PROPOSAL_MULTI_CHOICE = (
    "0xc950294fd8c00b2901026b62b568b01923e62166fca1e96d738f4a27bdf26faf"
)


@pytest.fixture
def snapshot_single_choice(voter_msig):
    voter_msig.init_snapshot(PROPOSAL_SINGLE_CHOICE)
    return voter_msig.snapshot


@pytest.fixture
def snapshot_multi_choice(voter_msig):
    voter_msig.init_snapshot(PROPOSAL_MULTI_CHOICE)
    return voter_msig.snapshot
