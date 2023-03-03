import pytest
import eth

import boa

INVALID_ADDRESS = pytest.ZERO_ADDRESS
VALID_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


def test_cannot_deploy_with_invalid_nft_address():
    with pytest.raises(eth.exceptions.Revert):
        boa.load("contracts/Vault.vy", INVALID_ADDRESS)


def test_deployment_sets_nft_address(vault, nft):
    assert vault.NFT() == nft.address


def test_operator_can_set_alchemist(vault, owner):
    assert vault.is_operator(owner)
    assert vault.alchemist() != VALID_ADDRESS

    vault.set_alchemist(VALID_ADDRESS)
    alchemist = vault.alchemist()

    assert alchemist == VALID_ADDRESS


def test_operator_cannot_set_alchemist_to_zero_address(vault, owner):
    assert vault.is_operator(owner)

    with boa.reverts():
        vault.set_alchemist(pytest.ZERO_ADDRESS)


def test_operator_cannot_set_alchemist_to_current_alchemist(vault, owner):
    assert vault.is_operator(owner)

    current_alchemist = vault.alchemist()
    assert current_alchemist != pytest.ZERO_ADDRESS

    with boa.reverts("same as current"):
        vault.set_alchemist(current_alchemist)


def test_non_operator_cannot_set_alchemist(vault, alice):
    assert not vault.is_operator(alice)

    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            vault.set_alchemist(VALID_ADDRESS)


def test_operator_can_set_fund_receiver(vault, owner):
    assert vault.is_operator(owner)
    assert vault.fund_receiver() != VALID_ADDRESS

    vault.set_fund_receiver(VALID_ADDRESS)
    fund_receiver = vault.fund_receiver()

    assert fund_receiver == VALID_ADDRESS


def test_operator_cannot_set_fund_receiver_to_zero_address(vault, owner):
    assert vault.is_operator(owner)

    with boa.reverts():
        vault.set_fund_receiver(pytest.ZERO_ADDRESS)


def test_operator_cannot_set_fund_receiver_to_current(vault, owner):
    assert vault.is_operator(owner)

    current_fund_receiver = vault.fund_receiver()
    assert current_fund_receiver != pytest.ZERO_ADDRESS

    with boa.reverts("same as current"):
        vault.set_fund_receiver(current_fund_receiver)


def test_non_operator_cannot_set_fund_receiver(vault, alice):
    assert not vault.is_operator(alice)

    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            vault.set_fund_receiver(VALID_ADDRESS)
