import pytest
from brownie import chain


def test_lock(vault, bal):
    vault.init_balancer()

    bal_before_bal = bal.balanceOf(vault)
    bal_before_vebal = vault.balancer.vebal.balanceOf(vault)

    vault.balancer.lock_bal(mantissa_bal=bal_before_bal)

    assert vault.balancer.vebal.balanceOf(vault) > bal_before_vebal
    assert bal.balanceOf(vault) < bal_before_bal
