from helpers.addresses import registry


def test_set_rate_model(rari):
    for label, addr in registry.eth.rari.items():
        if label.endswith('-22'):
            rari.ftoken_set_rate_model(
                addr, registry.eth.fei.jump_rate_model_fei_eth
            )
            break
