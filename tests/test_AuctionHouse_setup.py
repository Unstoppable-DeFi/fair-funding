import boa
import pytest
import eth

INVALID_RESERVE_PRICE = 0
VALID_RESERVE_PRICE = 10**18
INVALID_ADDRESS = pytest.ZERO_ADDRESS
VALID_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


def test_cannot_deploy_with_reserve_price_zero(owner, weth, nft):
    with pytest.raises(eth.exceptions.Revert):
        boa.load(
            "contracts/AuctionHouse.vy",
            weth,
            nft,
            0,
            100,
            INVALID_RESERVE_PRICE,
            owner,
            VALID_ADDRESS,
        )


def test_cannot_deploy_with_invalid_weth_address(owner, nft):
    with pytest.raises(eth.exceptions.Revert):
        boa.load(
            "contracts/AuctionHouse.vy",
            INVALID_ADDRESS,
            nft,
            0,
            100,
            VALID_RESERVE_PRICE,
            owner,
            VALID_ADDRESS,
        )


def test_cannot_deploy_with_invalid_nft_address(owner, weth):
    with pytest.raises(eth.exceptions.Revert):
        boa.load(
            "contracts/AuctionHouse.vy",
            weth,
            INVALID_ADDRESS,
            0,
            100,
            VALID_RESERVE_PRICE,
            owner,
            VALID_ADDRESS,
        )


def test_cannot_deploy_with_invalid_fallback_receiver_address(weth, nft):
    with pytest.raises(eth.exceptions.Revert):
        boa.load(
            "contracts/AuctionHouse.vy",
            weth,
            nft,
            0,
            100,
            VALID_RESERVE_PRICE,
            INVALID_ADDRESS,
            VALID_ADDRESS,
        )


def test_cannot_deploy_with_invalid_token_ids(weth, nft):
    start_id = 2
    max_id = 1
    with pytest.raises(eth.exceptions.Revert):
        boa.load(
            "contracts/AuctionHouse.vy",
            weth,
            nft,
            start_id,
            max_id,
            VALID_RESERVE_PRICE,
            INVALID_ADDRESS,
            VALID_ADDRESS,
        )


def test_cannot_deploy_with_invalid_vault_address():
    with pytest.raises(eth.exceptions.Revert):
        boa.load(
            "contracts/AuctionHouse.vy",
            VALID_ADDRESS,
            VALID_ADDRESS,
            0,
            1,
            VALID_RESERVE_PRICE,
            VALID_ADDRESS,
            INVALID_ADDRESS,
        )


def test_auctionhouse_deployed(house):
    assert house.address != pytest.ZERO_ADDRESS


def test_deployment_sets_reserve_price(owner, weth, nft):
    reserve_price = 123
    house = boa.load(
        "contracts/AuctionHouse.vy",
        weth,
        nft,
        0,
        100,
        reserve_price,
        owner,
        VALID_ADDRESS,
    )
    assert house.RESERVE_PRICE() == reserve_price


def test_deployment_sets_weth_address(house, weth):
    assert house.WETH() == weth.address


def test_deployment_sets_nft_address(house, nft):
    assert house.NFT() == nft.address


def test_deployment_sets_vault_address(house, mock_vault):
    assert house.vault() == mock_vault.address


def test_deployment_sets_fallback_receiver_address(owner, house):
    assert house.FALLBACK_RECEIVER() == owner


def test_deployment_sets_start_token_id(house, weth, nft, owner):
    start_token = 2
    house = boa.load(
        "contracts/AuctionHouse.vy",
        weth,
        nft,
        start_token,
        100,
        VALID_RESERVE_PRICE,
        owner,
        VALID_ADDRESS,
    )
    assert house.current_epoch_token_id() == start_token


def test_deployment_sets_start_token_id(house, weth, nft, owner):
    max_token = 55
    house = boa.load(
        "contracts/AuctionHouse.vy",
        weth,
        nft,
        0,
        max_token,
        VALID_RESERVE_PRICE,
        owner,
        VALID_ADDRESS,
    )
    assert house.max_token_id() == max_token


def test_deployment_sets_owner(house, owner):
    assert house.owner() == owner


def test_owner_can_set_vault(house, owner):
    assert house.owner() == owner

    before = house.vault()

    house.set_vault(owner)

    after = house.vault()

    assert after != before
    assert after == owner


def test_non_owner_cannot_set_vault(house, alice):
    assert house.owner() != alice

    with boa.env.prank(alice):
        with boa.reverts("unauthorized"):
            house.set_vault(alice)


def test_cannot_set_vault_to_zero_address(house, owner):
    assert house.owner() == owner

    with boa.reverts("vault cannot be zero address"):
        house.set_vault(pytest.ZERO_ADDRESS)
