import pytest
import boa

def timetravel(to):
    boa.env.vm.patch.timestamp = to


def test_start_sets_epoch_start(house):
    before = house.epoch_start()
    start = boa.env.vm.patch.timestamp + 10 * 60
    assert before != start

    house.start_auction(start)

    assert house.epoch_start() == start


def test_start_sets_epoch_end(house):
    before = house.epoch_end()
    start = boa.env.vm.patch.timestamp + 10 * 60
    epoch_length = house.EPOCH_LENGTH()

    assert before != start + epoch_length

    house.start_auction(start)

    assert house.epoch_end() == start + epoch_length


def test_start_without_explicit_value_starts_now(house):
    house.start_auction(0)
    assert house.epoch_start() == boa.env.vm.patch.timestamp


def test_cannot_start_in_the_past(house):
    with boa.reverts("cannot start in the past"):
        house.start_auction(boa.env.vm.patch.timestamp - 1)


def test_cannot_restart_when_started(house):
    house.start_auction(0)

    with boa.reverts("cannot restart auction"):
        house.start_auction(boa.env.vm.patch.timestamp + 10 * 60)


def test_cannot_restart_after_ended(house):
    assert house.max_token_id() == 1
    house.start_auction(0)
    timetravel(house.epoch_end() + 1)
    house.settle()
    timetravel(house.epoch_end() + 1)
    house.settle()
    assert house.epoch_end() == 0
    # Auction has ended!

    with boa.reverts("cannot restart auction"):
        house.start_auction(0)


def test_cannot_restart_between_epochs(house):
    house.start_auction(0)
    boa.env.vm.patch.timestamp = house.epoch_end() + 1

    with boa.reverts("cannot restart auction"):
        house.start_auction(0)


def test_NON_owner_cannot_start(house, alice):
    assert house.owner() != alice

    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            house.start_auction(0)
