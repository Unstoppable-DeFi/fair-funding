import pytest
import boa
from vyper.utils import checksum_encode


def pytest_configure():
    pytest.ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
    pytest.WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    pytest.ALCX_YIELD_TOKEN = "0xa258C4606Ca8206D8aA700cE2143D7db854D168c"
    pytest.ALETH = "0x0100546F2cD4C9D97f798fFC9755E47865FF7Ee6"


# ----------
#  Accounts
# ----------
OWNER = boa.env.generate_address("owner")
boa.env.eoa = OWNER


@pytest.fixture(scope="session")
def owner():
    return OWNER


@pytest.fixture(scope="session")
def alice():
    return boa.env.generate_address("alice")


@pytest.fixture(scope="session")
def bob():
    return boa.env.generate_address("bob")


# -----------
#  Contracts
# -----------
@pytest.fixture(scope="session")
def house_snapshot(owner, weth_snapshot, nft_snapshot, mock_vault_snapshot):
    return boa.load(
        "contracts/AuctionHouse.vy",
        weth_snapshot,
        nft_snapshot,
        0,  # start_token_id
        1,  # max_token_id
        10**18,  # reserve_price 1ETH,
        owner,
        mock_vault_snapshot,
    )


@pytest.fixture()
def house(house_snapshot):
    with boa.env.anchor():
        yield house_snapshot


@pytest.fixture(scope="session")
def weth_snapshot(alice, bob):
    weth = boa.load(
        "contracts/testing/token/ERC20.vy",
        "wrapped ETH",
        "WETH",
        18,
        10000 * 10**18,
        override_address=pytest.WETH,
    )
    weth.transfer(alice, 10 * 10**18)
    weth.transfer(bob, 10 * 10**18)
    return weth


@pytest.fixture()
def weth(weth_snapshot):
    with boa.env.anchor():
        yield weth_snapshot


@pytest.fixture(scope="session")
def mock_migrator_snapshot():
    return boa.load("contracts/testing/MockMigrator.vy")


@pytest.fixture()
def mock_migrator(mock_migrator_snapshot):
    with boa.env.anchor():
        yield mock_migrator_snapshot


@pytest.fixture(scope="session")
def nft_snapshot():
    nft = boa.load("contracts/testing/token/ERC721.vy")
    return nft


@pytest.fixture()
def nft(nft_snapshot):
    with boa.env.anchor():
        yield nft_snapshot


@pytest.fixture(scope="session")
def vault_snapshot(nft_snapshot):
    return boa.load("contracts/Vault.vy", nft_snapshot)


@pytest.fixture()
def vault(vault_snapshot):
    with boa.env.anchor():
        yield vault_snapshot


@pytest.fixture(scope="session")
def mock_vault_snapshot():
    return boa.load("contracts/testing/MockVault.vy")


@pytest.fixture()
def mock_vault(mock_vault_snapshot):
    with boa.env.anchor():
        yield mock_vault_snapshot


@pytest.fixture(scope="session")
def mock_alchemist_snapshot():
    return boa.load("contracts/testing/MockAlchemist.vy")


@pytest.fixture()
def alchemist(mock_alchemist_snapshot):
    with boa.env.anchor():
        yield mock_alchemist_snapshot


# -----------
#    setup
# -----------
@pytest.fixture(scope="session", autouse=True)
def setup(
    weth_snapshot,
    house_snapshot,
    nft_snapshot,
    vault_snapshot,
    mock_alchemist_snapshot,
    owner,
    alice,
    bob,
):
    weth_snapshot.approve(house_snapshot, weth_snapshot.balanceOf(owner))

    with boa.env.prank(alice):
        weth_snapshot.approve(house_snapshot, weth_snapshot.balanceOf(alice))

    with boa.env.prank(bob):
        weth_snapshot.approve(house_snapshot, weth_snapshot.balanceOf(bob))

    nft_snapshot.DEBUG_transferMinter(house_snapshot)
    vault_snapshot.set_alchemist(mock_alchemist_snapshot)
