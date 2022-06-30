import pytest


@pytest.fixture
def rari(dev):
    dev.init_rari()
    return dev.rari
