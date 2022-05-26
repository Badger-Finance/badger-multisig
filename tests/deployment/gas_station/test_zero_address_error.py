import brownie


def test_zero_address_error(gas_station):
    with brownie.reverts('typed error: 0xd92e233d'): # ZeroAddress
        gas_station.withdraw(gas_station.balance(), brownie.ZERO_ADDRESS)
