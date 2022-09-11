import brownie


def test_sweep_erc20_to_owner(dai, gas_station):
    # 'accidentally' transfer some erc20s to the contract
    dai._mint_for_testing(gas_station, 12345e18)

    bal_before = dai.balanceOf(gas_station.owner())
    # call to sweep them to the owner
    gas_station.sweep(dai, gas_station.owner())
    assert dai.balanceOf(gas_station.owner()) > bal_before


def test_sweep_erc20_to_random(dai, gas_station, random):
    # 'accidentally' transfer some erc20s to the contract
    dai._mint_for_testing(gas_station, 12345e18)

    bal_before = dai.balanceOf(random)
    # call to sweep them to the owner
    gas_station.sweep(dai, random)
    assert dai.balanceOf(random) > bal_before


def test_sweep_erc20_from_random(dai, gas_station, random):
    # 'accidentally' transfer some erc20s to the contract
    dai._mint_for_testing(gas_station, 12345e18)

    bal_before = dai.balanceOf(gas_station.owner())
    # call to sweep them to the owner
    with brownie.reverts("Only callable by owner"):
        gas_station.sweep(dai, gas_station.owner(), {"from": random})
    assert dai.balanceOf(gas_station.owner()) == bal_before
