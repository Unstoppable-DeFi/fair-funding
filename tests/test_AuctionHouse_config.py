import boa


def test_owner_can_suggest_new_admin(house, owner, alice):
    assert house.owner() == owner

    house.suggest_owner(alice)
    assert house.suggested_owner() == alice


def test_NON_owner_cannot_suggest_new_owner(house, alice):
    assert house.owner() != alice

    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            house.suggest_owner(alice)


def test_suggested_owner_can_accept_and_become_new_owner(house, owner, alice):
    house.suggest_owner(alice)

    assert house.owner() != alice
    assert house.suggested_owner() == alice

    with boa.env.prank(alice):
        house.accept_ownership()

    assert house.owner() == alice


def test_NON_suggested_owner_cannot_call_accept_ownership(house, alice, bob):
    house.suggest_owner(alice)

    assert house.suggested_owner() != bob

    with boa.env.prank(bob):
        with boa.reverts("unauthorized"):
            house.accept_ownership()


def test_max_token_id_can_be_adjusted(house):
    before = house.max_token_id()
    new_token_id = 123
    assert new_token_id != before

    house.set_max_token_id(new_token_id)

    after = house.max_token_id()

    assert after == new_token_id


def test_max_token_id_cannot_be_set_to_invalid_value(house):
    # move 1 epoch in
    boa.env.vm.patch.timestamp = house.epoch_end() + 1
    house.settle()

    current = house.current_epoch_token_id()
    new_max_token_id = current - 1
    assert new_max_token_id != house.max_token_id()

    with boa.reverts("cannot set max < current"):
        house.set_max_token_id(new_max_token_id)


def test_NON_owner_cannot_adjust_max_token_id(house, alice):
    assert house.owner() != alice
    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            house.set_max_token_id(123)
