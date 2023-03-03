import pytest

import boa


def timetravel(to):
    boa.env.vm.patch.timestamp = to


def test_settle_sends_nft_to_winner(house, alice, nft):
    house.start_auction(0)
    token_id = house.current_epoch_token_id()

    with boa.env.prank(alice):
        house.bid(token_id, house.RESERVE_PRICE())

    with boa.reverts():  # invalid token id, owner == 0x0
        nft.ownerOf(token_id)

    assert house.highest_bidder() == alice

    timetravel(house.epoch_end() + 1)

    house.settle()

    assert nft.ownerOf(token_id) == alice


def test_settle_resets_highest_bid(house):
    house.start_auction(0)
    house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())
    timetravel(house.epoch_end() + 1)

    assert house.highest_bid() != 0
    house.settle()
    assert house.highest_bid() == 0


def test_settle_resets_highest_bidder(house):
    house.start_auction(0)
    house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())
    timetravel(house.epoch_end() + 1)

    assert house.highest_bidder() != pytest.ZERO_ADDRESS
    house.settle()
    assert house.highest_bidder() == pytest.ZERO_ADDRESS


def test_settle_sends_nft_to_fallback_address_if_no_bid(owner, house, nft):
    house.start_auction(0)
    timetravel(house.epoch_end() + 1)

    token_id = house.current_epoch_token_id()

    assert house.highest_bidder() == pytest.ZERO_ADDRESS
    house.settle()
    assert nft.ownerOf(token_id) == owner


def test_cant_settle_before_epoch_over(house):
    house.start_auction(0)

    with boa.reverts("epoch not over"):
        house.settle()


def test_settle_starts_increments_token_id(house):
    house.start_auction(0)
    first_token_id = house.current_epoch_token_id()
    timetravel(house.epoch_end() + 1)
    house.settle()

    second_token_id = house.current_epoch_token_id()

    assert second_token_id == first_token_id + 1


def test_settle_sets_epoch_start(house):
    house.start_auction(0)
    first_epoch_start = house.epoch_start()

    t = house.epoch_end() + 1
    timetravel(t)

    house.settle()
    second_epoch_start = house.epoch_start()

    assert second_epoch_start != first_epoch_start
    assert second_epoch_start == t


def test_settle_sets_epoch_end(house):
    house.start_auction(0)
    first_epoch_end = house.epoch_end()

    t = house.epoch_end() + 1
    timetravel(t)

    house.settle()
    second_epoch_end = house.epoch_end()

    assert second_epoch_end != first_epoch_end
    assert second_epoch_end == t + house.EPOCH_LENGTH()


def test_settle_ends_auction_when_all_tokens_sold(house):
    house.start_auction(0)
    timetravel(house.epoch_end() + 1)
    house.settle()
    timetravel(house.epoch_end() + 1)
    house.settle()  # settle epoch 2, don't start new one

    assert house.current_epoch_token_id() == house.max_token_id()
    assert house.epoch_start() == 0
    assert house.epoch_end() == 0


def test_settle_approves_weth_to_vault(house, weth, mock_vault):
    house.start_auction(0)
    house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())
    timetravel(house.epoch_end() + 1)

    allowance_before = weth.allowance(house, mock_vault)

    bid = house.highest_bid()
    house.settle()

    assert house.WETH() == weth.address
    allowance_after = weth.allowance(house, mock_vault)

    assert allowance_after == allowance_before + bid


def test_settle_calls_vault_deposit(house, alice, mock_vault):
    house.start_auction(0)
    token_id = house.current_epoch_token_id()
    with boa.env.prank(alice):
        house.bid(token_id, house.RESERVE_PRICE())

    timetravel(house.epoch_end() + 1)

    vault_amount_before = mock_vault.amount()
    vault_token_id_before = mock_vault.token_id()
    assert vault_amount_before != house.RESERVE_PRICE()
    assert vault_token_id_before != token_id

    house.settle()

    vault_amount_after = mock_vault.amount()
    vault_token_id_after = mock_vault.token_id()

    assert vault_amount_after == house.RESERVE_PRICE()
    assert vault_token_id_after == token_id


def test_settle_does_not_calls_vault_deposit_when_no_bids(house, alice, mock_vault):
    house.start_auction(0)
    token_id = house.current_epoch_token_id()

    timetravel(house.epoch_end() + 1)

    vault_amount_before = mock_vault.amount()
    vault_token_id_before = mock_vault.token_id()
    assert vault_amount_before != house.RESERVE_PRICE()
    assert vault_token_id_before != token_id

    house.settle()

    vault_amount_after = mock_vault.amount()
    vault_token_id_after = mock_vault.token_id()

    assert vault_amount_after == vault_amount_before
    assert vault_token_id_after == vault_token_id_before
