import boa
import pytest
import math

AMOUNT = 123 * 10**18


def test_liquidate_calls_alcx_liquidate(vault, alchemist, nft, owner, weth):
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, 0)
    weth.approve(vault, AMOUNT)
    alchemist.eval(f"self.total_value = { AMOUNT }")
    vault.add_depositor(owner)
    vault.register_deposit(0, AMOUNT)
    alchemist.eval(f"self.debt = { math.floor(AMOUNT / 2)}")

    before_yield_token = alchemist.liquidate_yield_token()
    before_shares = alchemist.liquidate_shares()
    before_min_amount_out = alchemist.liquidate_min_amount_out()

    assert vault.alchemist() != pytest.ZERO_ADDRESS
    vault.liquidate(0, math.floor(AMOUNT / 2))

    after_yield_token = alchemist.liquidate_yield_token()
    after_shares = alchemist.liquidate_shares()
    after_min_amount_out = alchemist.liquidate_min_amount_out()

    assert before_yield_token != after_yield_token
    assert before_shares != after_shares
    assert before_min_amount_out != after_min_amount_out

    assert after_yield_token == pytest.ALCX_YIELD_TOKEN
    assert after_shares == AMOUNT / 2  # tokensPerShare = 1 in mock
    assert after_min_amount_out == 1  #


def test_liquidate_calls_alcx_withdraw_underlying(vault, alchemist, nft, owner, weth):
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, 0)
    weth.approve(vault, AMOUNT)
    alchemist.eval(f"self.total_value = { AMOUNT }")
    vault.add_depositor(owner)
    vault.register_deposit(0, AMOUNT)
    alchemist.eval(f"self.debt = { math.floor(AMOUNT / 2)}")

    before_yield_token = alchemist.wu_yield_token()
    before_shares = alchemist.wu_shares()
    before_recipient = alchemist.wu_recipient()
    before_min_amount_out = alchemist.wu_min_amount_out()

    assert vault.alchemist() != pytest.ZERO_ADDRESS
    min_out = math.floor(AMOUNT / 2)
    vault.liquidate(0, min_out)

    after_yield_token = alchemist.wu_yield_token()
    after_shares = alchemist.wu_shares()
    after_recipient = alchemist.wu_recipient()
    after_min_amount_out = alchemist.wu_min_amount_out()

    assert before_yield_token != after_yield_token
    assert before_shares != after_shares
    assert before_recipient != after_recipient
    assert before_min_amount_out != after_min_amount_out

    assert after_yield_token == pytest.ALCX_YIELD_TOKEN
    assert after_shares == AMOUNT / 2  # tokensPerShare = 1 in mock
    assert after_recipient == owner
    assert after_min_amount_out == min_out


def test_latest_collateralisation(vault, alchemist):
    alchemist.eval(f"self.total_value = {10 * 10**18}")
    alchemist.eval(f"self.debt = {5 * 10**18}")
    collateralisation = vault.internal._latest_collateralisation()
    assert collateralisation == 2 * 10**18

    alchemist.eval(f"self.total_value = {10 * 10**18}")
    alchemist.eval(f"self.debt = {10 * 10**18}")
    collateralisation = vault.internal._latest_collateralisation()
    assert collateralisation == 1 * 10**18

    alchemist.eval(f"self.total_value = {10 * 10**18}")
    alchemist.eval(f"self.debt = {1 * 10**18}")
    collateralisation = vault.internal._latest_collateralisation()
    assert collateralisation == 10 * 10**18


def test_latest_collateralisation_with_no_debt_reverts(vault, alchemist):
    alchemist.eval(f"self.total_value = {10 * 10**18}")
    alchemist.eval(f"self.debt = 0")

    with boa.reverts("zero debt"):
        vault.internal._latest_collateralisation()


def test_cannot_liquidate_already_liquidated(vault, nft, owner):
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, 0)
    vault.eval(
        f"self.positions[0] = Position({{token_id: 0, amount_deposited: {100*10**18}, amount_claimed: 0, shares_owned: {100*10**18}, is_liquidated: True }})"
    )

    with boa.reverts("position already liquidated"):
        vault.liquidate(0, 0)
