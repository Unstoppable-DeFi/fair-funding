import pytest
import math
import boa

TOKEN_ID = 0


@pytest.fixture(autouse=True)
def setup(weth, vault, nft, owner):
    weth.transfer(vault, 1 * 10**18)
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, TOKEN_ID)
    vault.eval(
        f"self.positions[0] = Position({{token_id: {TOKEN_ID}, amount_deposited: {1*10**18}, amount_claimed: 0, shares_owned: {1*10**18}, is_liquidated: False}})"
    )
    vault.eval(f"self.amount_claimable_per_share = 0")
    vault.eval(f"self.total_shares = {10*10**18}")
    vault.eval(f"self._mark_as_claimable({1*10**18})")


def test_claim_transfers_correct_amount(vault, weth, owner, nft):
    amount = vault.claimable_for_token(TOKEN_ID)
    assert amount == 10**17  # 0.1 ETH

    balance_before = weth.balanceOf(owner)
    vault.claim(TOKEN_ID)
    balance_after = weth.balanceOf(owner)

    assert balance_after == balance_before + amount


def test_claim_records_claimed_amount_correctly(vault):
    claimed_amount_index = 2
    amount = vault.claimable_for_token(TOKEN_ID)

    claimed_amount_before = vault.positions(TOKEN_ID)[claimed_amount_index]
    vault.claim(TOKEN_ID)
    claimed_amount_after = vault.positions(TOKEN_ID)[claimed_amount_index]

    assert claimed_amount_after == claimed_amount_before + amount


def test_cannot_claim_if_not_owner(vault, alice, nft):
    assert nft.ownerOf(TOKEN_ID) != alice
    with boa.env.prank(alice):
        with boa.reverts("only token owner can claim"):
            vault.claim(TOKEN_ID)


def test_cannot_claim_if_liquidated(vault, owner, nft):
    assert nft.ownerOf(TOKEN_ID) == owner
    vault.eval(
        f"self.positions[0] = Position({{token_id: {TOKEN_ID}, amount_deposited: {1*10**18}, amount_claimed: 0, shares_owned: 0, is_liquidated: True}})"
    )

    to_claim = vault.eval(f"self.amount_claimable_per_share")
    assert to_claim > 0

    with boa.reverts("nothing to claim"):
        vault.claim(TOKEN_ID)


def test_owner_can_liquidate(vault, nft, owner, alchemist):
    assert nft.ownerOf(TOKEN_ID) == owner

    amount_deposited = vault.eval(f"self.positions[0].amount_deposited")
    assert amount_deposited == 1 * 10**18
    alchemist.eval(f"self.total_value = { amount_deposited }")
    alchemist.eval(f"self.debt = { math.floor(amount_deposited / 2) }")

    is_liquidated = vault.eval(f"self.positions[0].is_liquidated")
    assert is_liquidated == False

    vault.liquidate(TOKEN_ID, 0)

    is_liquidated = vault.eval(f"self.positions[0].is_liquidated")
    assert is_liquidated == True


def test_non_owner_cannot_liquidate(vault, alice, nft):
    assert nft.ownerOf(TOKEN_ID) != alice
    with boa.env.prank(alice):
        with boa.reverts("only token owner can liquidate"):
            vault.liquidate(TOKEN_ID, 1)
