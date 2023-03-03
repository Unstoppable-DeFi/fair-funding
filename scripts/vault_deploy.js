const hre = require("hardhat");

async function main() {

    const nft_address = "0xc3BEA780Ab5aECa4F1c73fa83A35b8a54bCCCC1a"

    const VAULT_FAC = await hre.ethers.getContractFactory("Vault")
    const vault = await VAULT_FAC.deploy(nft_address)
    await vault.deployed()
    console.log("vault:", vault.address)
    console.log("with nft:", nft_address)

}


main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});