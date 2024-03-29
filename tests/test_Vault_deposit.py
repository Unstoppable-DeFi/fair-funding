import pytest
import boa

EXISTING_TOKEN_ID = 1
NON_EXISTING_TOKEN_ID = 999

AMOUNT = 12345 * 10**18


@pytest.fixture(autouse=True)
def approve(weth, vault, owner):
    weth.approve(vault, AMOUNT*2)
    vault.add_depositor(owner)


def test_register_transfers_weth_to_vault(weth, vault, nft, owner, alchemist):
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, EXISTING_TOKEN_ID)
    alchemist.eval(f"self.total_value = {AMOUNT}")

    caller_balance_before = weth.balanceOf(owner)
    vault_balance_before = weth.balanceOf(vault)

    vault.register_deposit(EXISTING_TOKEN_ID, AMOUNT)

    caller_balance_after = weth.balanceOf(owner)
    vault_balance_after = weth.balanceOf(vault)

    assert caller_balance_after == caller_balance_before - AMOUNT
    assert vault_balance_after == vault_balance_before + AMOUNT


def test_register_initializes_position_correctly(vault, nft, owner, alchemist):
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, EXISTING_TOKEN_ID)
    alchemist.eval(f"self.total_value = {AMOUNT}")
    before = vault.positions(EXISTING_TOKEN_ID)
    assert before == (0, 0, 0, 0, 0)

    vault.register_deposit(EXISTING_TOKEN_ID, AMOUNT)

    after = vault.positions(EXISTING_TOKEN_ID)

    assert after == (EXISTING_TOKEN_ID, AMOUNT, 0, AMOUNT, False)


def test_register_records_total_shares(vault, nft, owner, alchemist):
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, EXISTING_TOKEN_ID)
    alchemist.eval(f"self.total_value = {AMOUNT}")

    before = vault.total_shares()

    vault.register_deposit(EXISTING_TOKEN_ID, AMOUNT)

    after = vault.total_shares()

    assert after == before + AMOUNT


def test_register_only_once_per_token(vault, nft, owner, weth, alchemist):
    weth.approve(vault, 2*AMOUNT)
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, EXISTING_TOKEN_ID)
    alchemist.eval(f"self.total_value = {2*AMOUNT}")

    vault.register_deposit(EXISTING_TOKEN_ID, AMOUNT)

    with boa.reverts("can only deposit once per token"):
        vault.register_deposit(EXISTING_TOKEN_ID, AMOUNT)


def test_cannot_register_with_invalid_token_id(vault, nft):
    assert nft.idToOwner(NON_EXISTING_TOKEN_ID) == pytest.ZERO_ADDRESS

    with boa.reverts():
        vault.register_deposit(NON_EXISTING_TOKEN_ID, AMOUNT)


def test_operator_can_call_deposit(vault, owner, nft, alchemist):
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, EXISTING_TOKEN_ID)
    alchemist.eval(f"self.total_value = {AMOUNT}")

    assert vault.is_operator(owner)

    with boa.env.prank(owner):
        vault.register_deposit(EXISTING_TOKEN_ID, AMOUNT)


def test_register_reverts_when_no_new_debt_can_be_minted(vault, owner, nft, alchemist):
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, EXISTING_TOKEN_ID)
    alchemist.eval(f"self.total_value = {2*AMOUNT}")
    alchemist.eval(f"self.debt = {AMOUNT}")

    with boa.reverts("cannot mint new Alchemix debt"):
        vault.register_deposit(EXISTING_TOKEN_ID, AMOUNT)


def test_non_depositor_cannot_call_deposit(vault, alice, nft, owner):
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, EXISTING_TOKEN_ID)
    assert not vault.is_depositor(alice)

    with boa.env.prank(alice):
        with boa.reverts():
            vault.register_deposit(EXISTING_TOKEN_ID, AMOUNT)


def test_amount_claimable_per_share_is_adjusted_on_new_deposits(vault, alice, owner, nft, alchemist, weth):
    alchemist.eval(f"self.total_value = {2*AMOUNT}")
    alchemist.eval(f"self.debt = 0")

    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, EXISTING_TOKEN_ID)
    nft.mint(alice, EXISTING_TOKEN_ID+1)

    assert vault.amount_claimable_per_share() == 0

    vault.register_deposit(EXISTING_TOKEN_ID, AMOUNT)
    total_shares_before = vault.total_shares()

    weth.transfer(vault.address, 10 * 10**18)
    vault.internal._mark_as_claimable(10 * 10**18)

    claimable_before = vault.amount_claimable_per_share() 

    assert claimable_before > 0
    
    vault.register_deposit(EXISTING_TOKEN_ID+1, AMOUNT)

    total_shares_after = vault.total_shares()
    claimable_after = vault.amount_claimable_per_share()

    assert total_shares_after == total_shares_before * 2

    assert claimable_after == claimable_before / 2