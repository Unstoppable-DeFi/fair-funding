# Fair funding contest details

- Join [Sherlock Discord](https://discord.gg/MABEWyASkp)
- Submit findings using the issue page in your private contest repo (label issues as med or high)
- [Read for more details](https://docs.sherlock.xyz/audits/watsons)

# Resources

## About Fair Funding
- [Fair Funding Introduction Article](https://unstoppabledefi.medium.com/fair-funding-in-crypto-bc88d633646)
- [Fair Funding Campaign Article](https://unstoppabledefi.medium.com/fair-funding-campaign-662131dfa3f6)

## Integrations
- [Alchemix Finance](https://alchemix.fi)
- [Alchemix Contracts on Github](https://github.com/alchemix-finance/v2-foundry/tree/master/src)


# On-chain context

```
DEPLOYMENT: Ethereum Mainnet
ERC20: WETH
ERC721: MintableERC721 (part of this audit)
ERC777: none
FEE-ON-TRANSFER: none
REBASING TOKENS: none
ADMIN: trusted
EXTERNAL-ADMINS: trusted
```

## Priviledged Roles
### `AuctionHouse`: 
    1) `owner` can start/stop auction, refund highest bidder if needed and set the target vault contract

### `Vault`: 
    1) `is_operator`: can set the Alchemix Alchemist contract as well as the `fund_receiver` and add/remove other operators
    2) `is_depositor`: can deposit into the vault. In practice this will be the `AuctionHouse` contract.
    3) `migration_admin`: can set a migration contract and after 30 day timelock execute a migration. In practice this role will be handed over to the Alchemix Multisig and would only need to be used in case something significant changes at Alchemix. Since vault potentially holds an Alchemix position over a long time during which changes at Alchemix could happen, the `migration_admin` has complete control over the vault and its position after giving depositors a 30 day window to liquidate (or transfer with a flashloan) their position if they're not comfortable with the migration. `migration_admin` works under the same security and trust assumptions as the Alchemix (Proxy) Admins.

### `MintableERC721`:
    1) `owner`: one owner, in practice the `Vault` contract issuing a new token as receipt and control over a deposited position.


## Known Issues / Risks

During the auction phase all priviledged roles have to be trusted.  
Migration admin has to be trusted for the entire time, as long as there is an active position.  
Alchemix admins, protocol and underlying tokens have to be trusted.


# Audit scope

- `fair-funding/contracts/AuctionHouse.vy`
- `fair-funding/contracts/Vault.vy`
- `fair-funding/contracts/solidity/MintableERC721.sol`



