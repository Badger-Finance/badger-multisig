from helpers.addresses import registry


def test_set_cf(rari):
    for label, addr in registry.eth.rari.items():
        if label.endswith("-22"):
            rari.ftoken_set_cf(addr, 0.5)
            break
