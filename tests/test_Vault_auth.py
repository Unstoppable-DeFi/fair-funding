import boa
import pytest

def test_owner_can_add_operator(vault, owner, alice):
    assert vault.owner() == owner

    vault.add_operator(alice)

    assert vault.is_operator(alice) == True


def test_owner_can_remove_operator(vault, owner, alice):
    assert vault.owner() == owner
    vault.add_operator(alice)
    assert vault.is_operator(alice)

    vault.remove_operator(alice)

    assert vault.is_operator(alice) == False

def test_operator_cannot_remove_operator(vault, owner, alice):
    vault.add_operator(alice)
    assert vault.is_operator(alice)

    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            vault.remove_operator(alice)

    assert vault.is_operator(alice)


def test_non_operator_cannot_add_operator(vault, alice):
    assert vault.is_operator(alice) == False

    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            vault.add_operator(alice)


def test_owner_can_suggest_new_admin(vault, owner, alice):
    assert vault.migration_admin() == owner

    vault.suggest_migration_admin(alice)
    assert vault.suggested_migration_admin() == alice


def test_NON_owner_cannot_suggest_new_owner(vault, owner, alice):
    assert vault.migration_admin() == owner
    assert vault.migration_admin() != alice

    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            vault.suggest_migration_admin(alice)


def test_suggested_migration_admin_can_accept_and_become_new_migration_admin(vault, owner, alice):
    assert vault.migration_admin() == owner
    vault.suggest_migration_admin(alice)

    assert vault.migration_admin() != alice
    assert vault.suggested_migration_admin() == alice

    with boa.env.prank(alice):
        vault.accept_migration_admin()

    assert vault.migration_admin() == alice


def test_NON_suggested_admin_cannot_call_accept_ownership(vault, alice, bob):
    vault.suggest_migration_admin(alice)

    assert vault.suggested_migration_admin() != bob

    with boa.env.prank(bob):
        with boa.reverts("unauthorized"):
            vault.accept_migration_admin()


def test_owner_can_suggest_new_owner(vault, owner, alice):
    assert vault.owner() == owner

    vault.suggest_owner(alice)
    assert vault.suggested_owner() == alice


def test_NON_owner_cannot_suggest_new_owner(vault, owner, alice):
    assert vault.owner() == owner
    assert vault.owner() != alice

    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            vault.suggest_owner(alice)


def test_suggested_owner_can_accept_and_become_new_owner(vault, owner, alice):
    assert vault.owner() == owner
    vault.suggest_owner(alice)

    assert vault.owner() != alice
    assert vault.suggested_owner() == alice

    with boa.env.prank(alice):
        vault.accept_owner()

    assert vault.owner() == alice


def test_NON_suggested_owner_cannot_call_accept_ownership(vault, alice, bob):
    vault.suggest_owner(alice)

    assert vault.suggested_owner() != bob

    with boa.env.prank(bob):
        with boa.reverts("unauthorized"):
            vault.accept_owner()
