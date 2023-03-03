import pytest

import boa

AMOUNT = 123 * 10**18


@pytest.fixture(autouse=True)
def add_weth(vault, weth):
    weth.transfer(vault, 100 * 10**18)


def test_grants_allowance_to_alchemist(vault, weth, alchemist):
    before = weth.allowance(vault, alchemist)
    vault.internal._deposit_to_alchemist(AMOUNT)
    after = weth.allowance(vault, alchemist)

    assert after == before + AMOUNT


def test_register_calls_deposit_underlying_on_alcx(owner, vault, nft, weth, alchemist):
    vault.add_depositor(owner)
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, 0)
    weth.approve(vault, AMOUNT)
    alchemist.eval(f"self.total_value = {AMOUNT}")
    alchemist.eval(f"self.debt = 0")

    before_yield_token = alchemist.du_yield_token()
    before_amount = alchemist.du_amount()
    before_recipient = alchemist.du_recipient()
    before_min_amount_out = alchemist.du_min_amount_out()

    vault.register_deposit(0, AMOUNT)

    after_yield_token = alchemist.du_yield_token()
    after_amount = alchemist.du_amount()
    after_recipient = alchemist.du_recipient()
    after_min_amount_out = alchemist.du_min_amount_out()

    assert before_yield_token != after_yield_token
    assert before_amount != after_amount
    assert before_recipient != after_recipient
    assert before_min_amount_out != after_min_amount_out

    assert after_yield_token == pytest.ALCX_YIELD_TOKEN
    assert after_amount == AMOUNT
    assert after_recipient == vault.address
    assert after_min_amount_out == 1  # hardcoded to avoid complexity


def test_register_calls_mint_on_alcx(owner, nft, vault, alchemist, weth):
    vault.add_depositor(owner)
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, 0)
    weth.approve(vault, AMOUNT * 2)
    alchemist.eval(f"self.total_value = {AMOUNT * 2}")

    before_mint_amount = alchemist.mint_amount()
    before_mint_recipient = alchemist.mint_recipient()

    vault.register_deposit(0, AMOUNT * 2)

    after_mint_amount = alchemist.mint_amount()
    after_mint_recipient = alchemist.mint_recipient()

    assert after_mint_amount != before_mint_amount
    assert after_mint_recipient != before_mint_recipient

    assert after_mint_recipient == vault.fund_receiver()
    assert after_mint_amount == AMOUNT - 1


def test_withdraw_underlying_calls_alcx_withdraw(vault, alchemist):
    before_yield_token = alchemist.wu_yield_token()
    before_shares = alchemist.wu_shares()
    before_recipient = alchemist.wu_recipient()
    before_min_amount_out = alchemist.wu_min_amount_out()

    min_out = 1
    vault.withdraw_underlying_to_claim(AMOUNT, min_out)

    after_yield_token = alchemist.wu_yield_token()
    after_shares = alchemist.wu_shares()
    after_recipient = alchemist.wu_recipient()
    after_min_amount_out = alchemist.wu_min_amount_out()

    assert before_yield_token != after_yield_token
    assert before_shares != after_shares
    assert before_recipient != after_recipient
    assert before_min_amount_out != after_min_amount_out

    assert after_yield_token == pytest.ALCX_YIELD_TOKEN
    assert after_shares == AMOUNT
    assert after_recipient == vault.address
    assert after_min_amount_out == min_out


def test_amount_claimable_per_eth_is_set_correctly(vault):
    cases = [[100, 100, 1000000], [100, 200, 2000000], [200, 300, 1500000]]

    r = 0
    for c in cases:
        vault.eval(f"self.amount_claimable_per_share = 0")
        vault.eval(f"self.total_shares = {c[0]}")

        before = vault.amount_claimable_per_share()
        assert before == 0
        vault.internal._mark_as_claimable(c[1])
        after = vault.amount_claimable_per_share()

        assert after == c[2]


def test_claimable_amount_for_token_is_calculated_correctly(vault):
    vault.eval(
        f"self.positions[0] = Position({{token_id: 0, amount_deposited: {10**18}, amount_claimed: 0, shares_owned: {10**18}, is_liquidated: False}})"
    )
    vault.eval(f"self.total_shares = {100*10**18}")
    vault.internal._mark_as_claimable(10**18)

    amount = vault.claimable_for_token(0)

    assert amount == 10**16  # 0.01 ETH

    vault.eval(f"self.amount_claimable_per_share = 0")
    vault.eval(f"self.total_shares = {100*10**18}")
    vault.internal._mark_as_claimable(10 * 10**18)

    amount = vault.claimable_for_token(0)

    assert amount == 10**17  # 0.1 ETH

    vault.eval(f"self.amount_claimable_per_share = 0")
    vault.eval(f"self.total_shares = {1000*10**18}")
    vault.internal._mark_as_claimable(1 * 10**18)

    amount = vault.claimable_for_token(0)

    assert amount == 10**15  # 0.001 ETH

    vault.eval(
        f"self.positions[0] = Position({{token_id: 0, amount_deposited: {100*10**18}, amount_claimed: {50*10**18}, shares_owned: {100*10**18}, is_liquidated: False}})"
    )
    vault.eval(f"self.amount_claimable_per_share = 0")
    vault.eval(f"self.total_shares = {100*10**18}")
    vault.internal._mark_as_claimable(100 * 10**18)

    amount = vault.claimable_for_token(0)

    assert amount == 50 * 10**18  # 50 ETH


def test_claimable_amount_cannot_exceed_initial_deposit(vault):
    vault.eval(
        f"self.positions[0] = Position({{token_id: 0, amount_deposited: {100*10**18}, amount_claimed: {100*10**18}, shares_owned: {100*10**18}, is_liquidated: False}})"
    )
    vault.eval(f"self.amount_claimable_per_share = 0")
    vault.eval(f"self.total_shares = {100*10**18}")
    vault.internal._mark_as_claimable(100 * 10**18)

    amount = vault.claimable_for_token(0)

    assert amount == 0


def test_claimable_amount_for_invalid_token_is_zero(vault):
    vault.eval(
        f"self.positions[0] = Position({{token_id: 0, amount_deposited: {100*10**18}, amount_claimed: 0, shares_owned: 0, is_liquidated: False}})"
    )
    vault.eval(f"self.amount_claimable_per_share = 0")
    vault.eval(f"self.total_shares = {100*10**18}")
    vault.internal._mark_as_claimable(100 * 10**18)

    amount = vault.claimable_for_token(1)

    assert amount == 0


def test_claimable_amount_for_liquidated_token_is_zero(vault):
    vault.eval(
        f"self.positions[0] = Position({{token_id: 0, amount_deposited: {100*10**18}, amount_claimed: 0, shares_owned: 0, is_liquidated: True}})"
    )
    vault.eval(f"self.amount_claimable_per_share = 0")
    vault.eval(f"self.total_shares = {100*10**18}")
    vault.internal._mark_as_claimable(100 * 10**18)

    amount = vault.claimable_for_token(0)

    assert amount == 0


def test_calculate_mintable_amount(vault, alchemist):
    shares = 10 * 10**18
    alchemist.eval(f"self.total_value = {shares}")  # 10 ETH

    mintable_amount = vault.internal._calculate_mintable_amount(0)
    assert mintable_amount == 0

    alchemist.eval(f"self.debt = {0}")
    mintable_amount = vault.internal._calculate_mintable_amount(shares)
    assert mintable_amount == 5 * 10**18 - 1


def test_max_mintable_amount_is_calculated_correctly(vault, alchemist):
    alchemist.eval(f"self.total_value = {10 * 10**18}")  # 10 ETH

    alchemist.eval(f"self.debt = {0}")
    max_mintable = vault.internal._calculate_max_mintable_amount()
    assert max_mintable == 5 * 10**18 - 1

    alchemist.eval(f"self.debt = {5 * 10**18}")
    max_mintable = vault.internal._calculate_max_mintable_amount()
    assert max_mintable == 0

    alchemist.eval(f"self.debt = {1 * 10**18}")
    max_mintable = vault.internal._calculate_max_mintable_amount()
    assert max_mintable == 4 * 10**18 - 1

    alchemist.eval(f"self.debt = {1 * 10**18 + 1}")
    max_mintable = vault.internal._calculate_max_mintable_amount()
    assert max_mintable == 4 * 10**18 - 2


def test_calculate_amount_to_mint(vault, alchemist):
    shares = 4 * 10**18
    alchemist.eval(f"self.total_value = {100 * 10**18}")  # 10 ETH

    expected_mintable_by_shares = 2 * 10**18 - 1
    mintable_amount = vault.internal._calculate_mintable_amount(shares)
    assert mintable_amount == expected_mintable_by_shares

    alchemist.eval(f"self.debt = 0")
    expected_mintable_by_max = 50 * 10**18 - 1
    max_mintable = vault.internal._calculate_max_mintable_amount()
    assert max_mintable == expected_mintable_by_max

    amount_to_mint = vault.internal._calculate_amount_to_mint(shares)
    assert amount_to_mint == expected_mintable_by_shares

    alchemist.eval(f"self.debt = {49 * 10**18}")
    expected_mintable_by_max = 1 * 10**18 - 1
    max_mintable = vault.internal._calculate_max_mintable_amount()
    assert max_mintable == expected_mintable_by_max

    amount_to_mint = vault.internal._calculate_amount_to_mint(shares)
    assert amount_to_mint == expected_mintable_by_max
