import pytest
import boa

MAX_UINT256 = 2**256 - 1


def test_migrate_reverts_when_migrate_state_not_active(vault):
    assert vault.migration_active() > boa.env.vm.patch.timestamp

    with boa.reverts("migration not active"):
        vault.migrate()


def test_migration_admin_can_set_migrator(vault, owner, mock_migrator):
    assert vault.migration_admin() == owner
    vault.eval(f"self.migration_executed = True")

    assert vault.migrator() != mock_migrator.address
    assert vault.migration_active() != boa.env.vm.patch.timestamp + 30 * 60 * 60 * 24
    assert vault.migration_executed() != False

    vault.activate_migration(mock_migrator)

    assert vault.migrator() == mock_migrator.address
    assert vault.migration_active() == boa.env.vm.patch.timestamp + 30 * 60 * 60 * 24
    assert vault.migration_executed() == False


def test_migrate_calls_migrator(vault, owner, mock_migrator):
    vault.activate_migration(mock_migrator)
    boa.env.vm.patch.timestamp += 30 * 60 * 60 * 24

    assert vault.is_operator(owner)

    assert mock_migrator.was_called() == False

    vault.migrate()

    assert mock_migrator.was_called() == True


def test_migrate_sets_migration_executed(vault, owner, mock_migrator):
    vault.activate_migration(mock_migrator)
    boa.env.vm.patch.timestamp += 30 * 60 * 60 * 24

    assert vault.is_operator(owner)
    assert vault.migration_executed() == False

    vault.migrate()

    assert vault.migration_executed() == True


def test_cannot_execute_migration_twice(vault, owner, mock_migrator):
    vault.activate_migration(mock_migrator)
    boa.env.vm.patch.timestamp += 30 * 60 * 60 * 24

    assert vault.is_operator(owner)

    vault.migrate()

    with boa.reverts("migration already executed"):
        vault.migrate()


def test_admin_can_deactivate_migration(vault, owner, mock_migrator):
    assert vault.migration_admin() == owner
    vault.activate_migration(mock_migrator)

    assert vault.migration_active() < MAX_UINT256
    assert vault.migrator() != pytest.ZERO_ADDRESS

    vault.deactivate_migration()
    assert vault.migration_active() == MAX_UINT256
    assert vault.migrator() == pytest.ZERO_ADDRESS


def test_cannot_override_active_migration(vault, owner, mock_migrator):
    assert vault.migration_admin() == owner
    vault.activate_migration(mock_migrator)
    assert vault.migration_active() < MAX_UINT256  # migration active

    with boa.reverts("cannot override active migration"):
        vault.activate_migration(mock_migrator)
