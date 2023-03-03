import pytest
import math

AMOUNT = 100 * 10**18

TOKEN_ID = 0


@pytest.fixture(autouse=True)
def setup(nft, weth, owner, vault, alchemist):
    vault.add_depositor(owner)
    weth.approve(vault, AMOUNT)
    nft.DEBUG_transferMinter(owner)
    nft.mint(owner, TOKEN_ID)
    alchemist.eval(f"self.total_value = {AMOUNT}")


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


def test_register_deposit_emits_event(vault, owner):
    vault.register_deposit(TOKEN_ID, AMOUNT)
    assert emitted(vault, "Deposit", owner, TOKEN_ID, AMOUNT)


def test_minting_alchemix_debt_emits_event(vault, alice, alchemist):
    vault.internal._mint_from_alchemix(AMOUNT, alice)
    assert emitted(vault, "Funded", alice, AMOUNT)


def test_liquidate_emits_event(vault, owner, alchemist):
    alchemist.eval(f"self.total_value = { AMOUNT }")
    vault.register_deposit(0, AMOUNT)
    alchemist.eval(f"self.debt = { math.floor(AMOUNT / 2) }")
    min_weth_out = math.floor(AMOUNT / 2)
    vault.liquidate(TOKEN_ID, min_weth_out)

    assert emitted(vault, "Liquidated", TOKEN_ID, owner, min_weth_out)


def test_withdraw_to_claim_emits_event(vault):
    shares = 123
    min_weth_out = 234
    vault.withdraw_underlying_to_claim(shares, min_weth_out)

    assert emitted(vault, "Claimable", min_weth_out)


def test_claiming_emits_event(vault, owner):
    vault.register_deposit(TOKEN_ID, AMOUNT)
    vault.withdraw_underlying_to_claim(1, AMOUNT)
    amount = vault.claimable_for_token(TOKEN_ID)
    assert amount > 0
    vault.claim(TOKEN_ID)

    assert emitted(vault, "Claimed", TOKEN_ID, owner, amount)


def test_set_alchemist_emits_event(vault, owner, alice):
    vault.set_alchemist(alice)
    assert emitted(vault, "AlchemistUpdated", owner, alice)


def test_set_fund_receiver_emits_event(vault, owner, alice):
    vault.set_fund_receiver(alice)
    assert emitted(vault, "FundReceiverUpdated", owner, alice)


def test_deactivate_migration_emits_event(vault, owner, mock_migrator):
    vault.activate_migration(mock_migrator)

    vault.deactivate_migration()
    assert emitted(vault, "MigrationDeactivated")


def test_add_operator_emits_event(vault, owner, alice):
    vault.add_operator(alice)
    assert emitted(vault, "NewOperator", alice, owner)


def test_remove_operator_emits_event(vault, owner, alice):
    vault.add_operator(alice)

    vault.remove_operator(alice)
    assert emitted(vault, "OperatorRemoved", alice, owner)


def test_add_depositor_emits_event(vault, owner, alice):
    vault.add_depositor(alice)
    assert emitted(vault, "NewDepositor", alice, owner)


def test_remove_depositor_emits_event(vault, owner, alice):
    vault.add_depositor(alice)

    vault.remove_depositor(alice)
    assert emitted(vault, "DepositorRemoved", alice, owner)
