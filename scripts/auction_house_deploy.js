const hre = require("hardhat");
const ethers = require("ethers")

async function main() {

    const AUCTION_HOUSE_FAC = await hre.ethers.getContractFactory("AuctionHouse")

    // def __init__(
    //     _weth_address: address,
    const weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    //     _nft_address: address,
    const nft_address = "0xc3BEA780Ab5aECa4F1c73fa83A35b8a54bCCCC1a"
    //     _start_token_id: uint256,
    const start_token_id = 0
    //     _max_token_id: uint256,
    const max_token_id = 100
    //     _reserve_price: uint256,
    const reserve_price = ethers.utils.parseEther("1")
    //     _fallback_receiver: address,
    const fallback_receiver = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    //     _vault_address: address
    const vault_address = "0xAe9Ed85dE2670e3112590a2BB17b7283ddF44d9c"
    // ):


    const auction_house = await AUCTION_HOUSE_FAC.deploy(
        weth_address,
        nft_address,
        start_token_id,
        max_token_id,
        reserve_price,
        fallback_receiver,
        vault_address
    )
    await auction_house.deployed()
    console.log("auction_house:", auction_house.address)

}


main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});