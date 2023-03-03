import math
import pytest

import boa


@pytest.fixture(autouse=True)
def start(house):
    house.start_auction(0)


def timetravel(to):
    boa.env.vm.patch.timestamp = to


def test_cannot_bid_under_reserve_price(house):
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()

    assert reserve_price > 1

    with boa.reverts("reserve price not met"):
        house.bid(token_id, reserve_price - 1)


def test_cannot_bid_on_non_active_token_id(house):
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()

    with boa.reverts("token id not up for auction"):
        house.bid(token_id + 1, reserve_price)


def test_valid_bid_sets_highest_bid(house):
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()
    highest_bid = house.highest_bid()

    amount = max(reserve_price, highest_bid) * 2

    house.bid(token_id, amount)
    assert amount == house.highest_bid()


def test_valid_bid_sets_highest_bidder(house, alice):
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()
    highest_bid = house.highest_bid()
    highest_bidder = house.highest_bidder()
    assert highest_bidder != alice

    amount = max(reserve_price, highest_bid) * 2

    with boa.env.prank(alice):
        house.bid(token_id, amount)
        assert alice == house.highest_bidder()


def test_new_bid_has_to_be_higher_than_current_highest_bid(house):
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()
    highest_bid = house.highest_bid()

    amount = max(reserve_price, highest_bid) * 2

    house.bid(token_id, amount)
    assert house.highest_bid() > 0

    with boa.reverts("bid not high enough"):
        house.bid(token_id, house.highest_bid())


def test_min_bid_increment(house):
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()

    assert reserve_price > 0
    assert house.highest_bid() == 0

    house.bid(token_id, reserve_price)
    assert reserve_price == house.highest_bid()

    min_increment_pct = house.MIN_INCREMENT_PCT()

    invalid_amount = (
        math.floor(house.highest_bid() * (100 + min_increment_pct) / 100) - 1
    )
    assert invalid_amount > house.highest_bid()

    with boa.reverts("bid not high enough"):
        house.bid(token_id, invalid_amount)

    valid_amount = math.ceil(house.highest_bid() * (100 + min_increment_pct) / 100) + 1
    assert invalid_amount > house.highest_bid()

    house.bid(token_id, valid_amount)
    assert house.highest_bid() == valid_amount


def test_bid_transfers_weth(house, weth, alice):
    house_balance_before = weth.balanceOf(house)
    alice_balance_before = weth.balanceOf(alice)

    amount = house.RESERVE_PRICE()

    with boa.env.prank(alice):
        house.bid(house.current_epoch_token_id(), amount)

    house_balance_after = weth.balanceOf(house)
    alice_balance_after = weth.balanceOf(alice)

    assert house_balance_after == house_balance_before + amount
    assert alice_balance_after == alice_balance_before - amount


def test_last_bidder_gets_refunded(house, weth, alice, bob):
    amount = house.RESERVE_PRICE()

    alice_balance_initial = weth.balanceOf(alice)

    with boa.env.prank(alice):
        house.bid(house.current_epoch_token_id(), amount)

    with boa.env.prank(bob):
        house.bid(house.current_epoch_token_id(), amount * 2)

    alice_balance_after = weth.balanceOf(alice)

    assert alice_balance_after == alice_balance_initial


def test_cannot_bid_before_epoch_starts(house):
    timetravel(house.epoch_start() - 1)

    with boa.reverts("auction not in progress"):
        house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())


def test_cannot_bid_after_epoch_ends(house):
    timetravel(house.epoch_end() + 1)

    with boa.reverts("auction not in progress"):
        house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())


def test_bid_increases_epoch_end_by_buffer(house):
    epoch_end_before = house.epoch_end()
    timetravel(epoch_end_before - 1)

    house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())

    epoch_end_after = house.epoch_end()

    assert epoch_end_after != epoch_end_before
    assert epoch_end_after == boa.env.vm.patch.timestamp + house.TIME_BUFFER()


def test_owner_can_refund_highest_bidder(house, owner, alice, weth):
    amount = house.RESERVE_PRICE()

    with boa.env.prank(alice):
        house.bid(house.current_epoch_token_id(), amount)

    timetravel(house.epoch_end() + 1)

    balance_bidder_before = weth.balanceOf(alice)
    balance_house_before = weth.balanceOf(house)

    house.refund_highest_bidder()

    balance_bidder_after = weth.balanceOf(alice)
    balance_house_after = weth.balanceOf(house)

    assert balance_bidder_after == balance_bidder_before + amount
    assert balance_house_after == balance_house_before - amount


def test_non_owner_cannot_refund_highest_bidder(house, alice):
    amount = house.RESERVE_PRICE()

    with boa.env.prank(alice):
        house.bid(house.current_epoch_token_id(), amount)

    timetravel(house.epoch_end() + 1)

    assert house.owner() != alice
    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            house.refund_highest_bidder()


def test_calling_refund_resets_bidder_and_highest_bid(house, owner):
    house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())
    timetravel(house.epoch_end() + 1)

    bid_before = house.highest_bid()
    bidder_before = house.highest_bidder()
    assert bid_before != 0
    assert bidder_before != pytest.ZERO_ADDRESS

    house.refund_highest_bidder()

    bid_after = house.highest_bid()
    bidder_after = house.highest_bidder()
    assert bid_after == 0
    assert bidder_after == pytest.ZERO_ADDRESS


def test_refund_cannot_be_called_while_epoch_in_progress(house):
    house.bid(house.current_epoch_token_id(), house.RESERVE_PRICE())

    with boa.reverts("epoch not over"):
        house.refund_highest_bidder()
