import pytest
import boa


def timetravel(to):
    boa.env.vm.patch.timestamp = to


def emitted(contract, event, *expected_params):
    logs = contract.get_logs()
    # print(logs)
    e = None

    for l in logs:
        if l.event_type.name == event:
            e = l
            break

    if e == None:
        print("actual  : ", logs)
        print("expected: ", event, expected_params)
        raise Exception(f"event {event} was not emitted")

    t_i = 0
    a_i = 0
    params = []
    # align the evm topic + args lists with the way they appear in the source
    # ex. Transfer(indexed address, address, indexed address)
    for is_topic, k in zip(e.event_type.indexed, e.event_type.arguments.keys()):
        if is_topic:
            params.append(e.topics[t_i])
            t_i += 1
        else:
            params.append(e.args[a_i])
            a_i += 1

    if len(params) != len(expected_params):
        print("actual  : ", params)
        print("expected: ", expected_params)
        raise Exception(f"event {event} emitted with wrong number of params")

    for i, _ in enumerate(params):
        if params[i] != expected_params[i]:
            print("actual  : ", params)
            print("expected: ", expected_params)
            raise Exception(f"event {event} emitted with wrong params")

    return True


def test_auction_start_emits_event(house, owner):
    house.start_auction(0)
    assert emitted(house, "AuctionStart", boa.env.vm.patch.timestamp, owner)


def test_bidding_emits_bid_event(house, owner):
    house.start_auction(0)
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()
    house.bid(token_id, reserve_price)
    assert emitted(house, "Bid", token_id, owner, reserve_price)


def test_overbidding_emits_bid_refunded_event(house, owner, alice):
    house.start_auction(0)
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()
    house.bid(token_id, reserve_price)

    with boa.env.prank(alice):
        house.bid(token_id, reserve_price * 2)

    assert emitted(house, "BidRefunded", token_id, owner, reserve_price)


def test_settle_emits_event(house, owner):
    house.start_auction(0)
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()
    house.bid(token_id, reserve_price)
    timetravel(house.epoch_end() + 1)
    house.settle()

    assert emitted(house, "AuctionSettled", token_id, owner, reserve_price)


def test_settle_without_bid_emits_event(house):
    house.start_auction(0)
    token_id = house.current_epoch_token_id()
    receiver = house.FALLBACK_RECEIVER()
    timetravel(house.epoch_end() + 1)
    house.settle()
    assert emitted(house, "AuctionSettledWithNoBid", token_id, receiver)


def test_bid_near_epoch_end_emits_auction_extended_event(house, owner):
    house.start_auction(0)
    token_id = house.current_epoch_token_id()
    reserve_price = house.RESERVE_PRICE()
    epoch_end_before = house.epoch_end()
    buffer = house.TIME_BUFFER()
    timetravel(epoch_end_before - 1)

    house.bid(token_id, reserve_price)

    assert emitted(house, "AuctionExtended", token_id, epoch_end_before - 1 + buffer)


def test_suggesting_new_owner_emits_event(house, owner, alice):
    house.suggest_owner(alice)
    assert emitted(house, "NewOwnerSuggested", owner, alice)


def test_accepting_ownership_emits_event(house, owner, alice):
    house.suggest_owner(alice)

    with boa.env.prank(alice):
        house.accept_ownership()

    assert emitted(house, "OwnershipTransferred", owner, alice)
