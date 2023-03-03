import boa

boa.env.fork(
    url="https://eth-mainnet.g.alchemy.com/v2/Av81aQS88N_SG0iwgWCQCAvFy4giDIKs"
)

weth = boa.load_partial("contracts/token/ERC20.vy").at(
    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
)

owner = boa.env.generate_address("owner")
boa.env.eoa = owner

# weth whale
with boa.env.prank("0x06920C9fC643De77B99cB7670A944AD31eaAA260"):
    weth.transfer(owner, 420000000000000000000)

# Alchemist Whitelist owner
# with boa.env.prank("0x9e2b6378ee8ad2A4A95Fe481d63CAba8FB0EBBF9"):
#     alchemistWhitelist.add(vault)

alchemist = boa.load_partial("contracts/testing/MockAlchemist.vy").at(
    "0x062Bf725dC4cDF947aa79Ca2aaCCD4F385b13b5c"
)

ALCX_YVWETH = boa.load_partial("contracts/token/ERC20.vy").at(
    "0xa258C4606Ca8206D8aA700cE2143D7db854D168c"
)

nft = boa.load("contracts/token/ERC721.vy")

vault = boa.load("contracts/Vault.vy")
