from helpers.addresses import registry


def test_pause(rari):
    for label, addr in registry.eth.rari.items():
        if label.endswith("-22"):
            if not rari.ftoken_is_paused(addr):
                rari.ftoken_pause(addr)
                break


def test_unpause(rari):
    for label, addr in registry.eth.rari.items():
        if label.endswith("-22"):
            if rari.ftoken_is_paused(addr):
                rari.ftoken_unpause(addr)
                break
