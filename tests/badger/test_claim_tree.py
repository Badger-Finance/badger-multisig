def test_claim_all(ibbtc_msig):
    ibbtc_msig.init_badger()
    ibbtc_msig.badger.claim_all()


def test_claim_all(dev):
    dev.init_badger()
    dev.badger.claim_all()
