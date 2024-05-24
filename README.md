<div align="center" style="margin-bottom:15px">
  <img height=80 src="https://badger.com/images/badger-logo.svg">
</div>

# Badger Multisig

This repo is where all EVM multisig operations take place for the Badger DAO.
It relies heavily on [`ganache-cli`](https://docs.nethereum.com/en/latest/ethereum-and-clients/ganache-cli/), [`eth-brownie`](https://github.com/eth-brownie/brownie), [`gnosis-py`](https://github.com/gnosis/gnosis-py) and a custom developed evolution of [`ape-safe`](https://github.com/banteg/ape-safe); [`great-ape-safe`](https://github.com/gosuto-ai/great-ape-safe).

A good overview of all its tickets and their status can be found here: https://github.com/orgs/Badger-Finance/projects/25.

Read more about the Badger DAO and its community at https://badger.com/.

## Installation

The recommended installation tool for this repository is [`poetry`](https://python-poetry.org/docs/):
```
poetry install
git submodule update --init --recursive --progress
```

In case of missing python versions, and depending on your setup, you might want to have a look at [`pyenv`](https://github.com/pyenv/pyenv).

Enter `poetry`'s virtual environment through `poetry shell`. You should now be able to run `brownie` from within this virtual environment. Type `exit` or ctrl-D to leave the environment.

Alternatively, you could use the `requirements.txt` (or `requirements-dev.txt` if you want to include testing packages) via `pip`: `pip install -r requirements.txt`.

### OpenSSL Deprecation (macOS)

The installation process might run into some OpenSSL issues (`fatal error: openssl/aes.h: No such file or directory`). Please see [the note on OpenSSL in the Vyper docs](https://docs.vyperlang.org/en/v0.1.0-beta.17/installing-vyper.html#installation) or [this related issue](https://github.com/ethereum/pyethereum/issues/292) in order to fix it.

### Arm Chipset Architecture (M1/M2)
MacBooks with arm chipsets have some additional challenges [[source]](https://github.com/psf/black/issues/2524).

In our case, since `eth-brownie` locks on this borked `regex==2021.10.8` [[source]](https://github.com/eth-brownie/brownie/blob/1eeb5b3a42509f14cdd2d269c5629cfeaf850fcc/requirements.txt#L193), we have to override `regex` after `poetry`'s lock. Go into the virtual environment created by `poetry` and install the next version of `regex`:
```
poetry shell
pip install regex==2021.10.21
```
You can ignore the following warning:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
eth-brownie 1.17.0 requires regex==2021.10.8, but you have regex 2021.10.21 which is incompatible.
```

### module 'rlp' has no attribute 'Serializable'
Another corner case you may encountered while trying to run `brownie console` or scripts is `AttributeError: module 'rlp' has no attribute 'Serializable'`. Solution can be found [here](https://lightrun.com/answers/apeworx-ape-docker-startup-error-attributeerror-module-rlp-has-no-attribute-serializable).

```
poetry shell
pip uninstall rlp --yes && pip install rlp==3.0.0
```

Warning can be ignored regarding pip's dependency resolver conflicts.

## Uninstall

Delete the virtual environment as such:
```
rm -rf `poetry env info -p`
```

## Multisig Addresses

| Label | Description | Address (Links) |
|-|-|-|
|`dev.badgerdao.eth`|Governance/admin rights; set parameters on vaults and strategies, queue/execute timelock txs, etc.|Mainnet: `0xB65cef03b9B89f99517643226d76e286ee999e77` ([Etherscan](https://etherscan.io/address/0xB65cef03b9B89f99517643226d76e286ee999e77), [Gnosis Safe](https://gnosis-safe.io/app/eth:0xB65cef03b9B89f99517643226d76e286ee999e77/), [Zapper](https://zapper.fi/account/0xB65cef03b9B89f99517643226d76e286ee999e77), [DeBank](https://debank.com/profile/0xB65cef03b9B89f99517643226d76e286ee999e77))|
|||Arbitrum: `0xb364bAb258ad35dd83c7dd4E8AC78676b7aa1e9F` ([Arbiscan](https://arbiscan.io/address/0xb364bAb258ad35dd83c7dd4E8AC78676b7aa1e9F), [Gnosis Safe](https://gnosis-safe.io/app/arb1:0xb364bAb258ad35dd83c7dd4E8AC78676b7aa1e9F/), [Zapper](https://zapper.fi/account/0xb364bAb258ad35dd83c7dd4E8AC78676b7aa1e9F), [DeBank](https://debank.com/profile/0xb364bAb258ad35dd83c7dd4E8AC78676b7aa1e9F))|
|||Binance Smart Chain: `0x329543f0F4BB134A3f7a826DC32532398B38a3fA` ([BscScan](https://bscscan.com/address/0x329543f0F4BB134A3f7a826DC32532398B38a3fA), [Gnosis Safe](https://gnosis-safe.io/app/bnb:0x329543f0F4BB134A3f7a826DC32532398B38a3fA/), [Zapper](https://zapper.fi/account/0x329543f0F4BB134A3f7a826DC32532398B38a3fA), [DeBank](https://debank.com/profile/0x329543f0F4BB134A3f7a826DC32532398B38a3fA))|
|||Polygon: `0x4977110Ed3CD5eC5598e88c8965951a47dd4e738` ([PolygonScan](https://polygonscan.com/address/0x4977110Ed3CD5eC5598e88c8965951a47dd4e738), [Gnosis Safe](https://gnosis-safe.io/app/matic:0x4977110Ed3CD5eC5598e88c8965951a47dd4e738/), [Zapper](https://zapper.fi/account/0x4977110Ed3CD5eC5598e88c8965951a47dd4e738), [DeBank](https://debank.com/profile/0x4977110Ed3CD5eC5598e88c8965951a47dd4e738))|
|||Fantom: `0x4c56ee3295042f8A5dfC83e770a21c707CB46f5b` ([FTMScan](https://ftmscan.com/address/0x4c56ee3295042f8A5dfC83e770a21c707CB46f5b), [Fantom Safe](https://safe.fantom.network/#/safes/0x4c56ee3295042f8A5dfC83e770a21c707CB46f5b/), [Zapper](https://zapper.fi/account/0x4c56ee3295042f8A5dfC83e770a21c707CB46f5b), [DeBank](https://debank.com/profile/0x4c56ee3295042f8A5dfC83e770a21c707CB46f5b))|
|||Optimism: `0x0D5eDB3ECbB15EF4EaD105c018fEd4e1d173B335` ([Optimistic Etherscan](https://optimistic.etherscan.io/address/0x0D5eDB3ECbB15EF4EaD105c018fEd4e1d173B335), [Gnosis Safe](https://gnosis-safe.io/app/oeth:0x0D5eDB3ECbB15EF4EaD105c018fEd4e1d173B335/), [Zapper](https://zapper.fi/account/0x0D5eDB3ECbB15EF4EaD105c018fEd4e1d173B335), [DeBank](https://debank.com/profile/0x0D5eDB3ECbB15EF4EaD105c018fEd4e1d173B335))|
|`techops.badgerdao.eth`|Controller for the DAO. Call internal system functions; set emission schedules.|Mainnet: `0x86cbD0ce0c087b482782c181dA8d191De18C8275` ([Etherscan](https://etherscan.io/address/0x86cbD0ce0c087b482782c181dA8d191De18C8275), [Gnosis Safe](https://gnosis-safe.io/app/eth:0x86cbD0ce0c087b482782c181dA8d191De18C8275/), [Zapper](https://zapper.fi/account/0x86cbD0ce0c087b482782c181dA8d191De18C8275), [DeBank](https://debank.com/profile/0x86cbD0ce0c087b482782c181dA8d191De18C8275))|
|||Arbitrum: `0x292549E6bd5a41aE4521Bb8679aDA59631B9eD4C` ([Arbiscan](https://arbiscan.io/address/0x292549E6bd5a41aE4521Bb8679aDA59631B9eD4C), [Gnosis Safe](https://gnosis-safe.io/app/arb1:0x292549E6bd5a41aE4521Bb8679aDA59631B9eD4C/), [Zapper](https://zapper.fi/account/0x292549E6bd5a41aE4521Bb8679aDA59631B9eD4C), [DeBank](https://debank.com/profile/0x292549E6bd5a41aE4521Bb8679aDA59631B9eD4C))|
|||Binance Smart Chain: `0x777061674751834993bfBa2269A1F4de5B4a6E7c` ([BscScan](https://bscscan.com/address/0x777061674751834993bfBa2269A1F4de5B4a6E7c), [Zapper](https://zapper.fi/account/0x777061674751834993bfBa2269A1F4de5B4a6E7c), [DeBank](https://debank.com/profile/0x777061674751834993bfBa2269A1F4de5B4a6E7c))|
|||Polygon: `0xeb7341c89ba46CC7945f75Bd5dD7a04f8FA16327` ([PolygonScan](https://polygonscan.com/address/0xeb7341c89ba46CC7945f75Bd5dD7a04f8FA16327), [Gnosis Safe](https://gnosis-safe.io/app/matic:0xeb7341c89ba46CC7945f75Bd5dD7a04f8FA16327/), [Zapper](https://zapper.fi/account/0xeb7341c89ba46CC7945f75Bd5dD7a04f8FA16327), [DeBank](https://debank.com/profile/0xeb7341c89ba46CC7945f75Bd5dD7a04f8FA16327))|
|||Fantom: `0x781E82D5D49042baB750efac91858cB65C6b0582` ([FTMScan](https://ftmscan.com/address/0x781E82D5D49042baB750efac91858cB65C6b0582), [Fantom Safe](https://safe.fantom.network/#/safes/0x781E82D5D49042baB750efac91858cB65C6b0582/), [Zapper](https://zapper.fi/account/0x781E82D5D49042baB750efac91858cB65C6b0582), [DeBank](https://debank.com/profile/0x781E82D5D49042baB750efac91858cB65C6b0582))|
|||Optimism: `0x8D05c5DA2a3Cb4BeB4C5EB500EE9e3Aa71670733` ([Optimistic Etherscan](https://optimistic.etherscan.io/address/0x8D05c5DA2a3Cb4BeB4C5EB500EE9e3Aa71670733), [Gnosis Safe](https://gnosis-safe.io/app/oeth:0x8D05c5DA2a3Cb4BeB4C5EB500EE9e3Aa71670733/), [Zapper](https://zapper.fi/account/0x8D05c5DA2a3Cb4BeB4C5EB500EE9e3Aa71670733), [DeBank](https://debank.com/profile/0x8D05c5DA2a3Cb4BeB4C5EB500EE9e3Aa71670733))|
|`treasuryvault.badgerdao.eth`|Treasury long-term holdings; bitcoin, ether (gas), treasury controlled liquidity (TCL), farming positions, uncirculating $BADGER.|Mainnet: `0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e` ([Etherscan](https://etherscan.io/address/0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e), [Gnosis Safe](https://gnosis-safe.io/app/eth:0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e/), [Zapper](https://zapper.fi/account/0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e), [DeBank](https://debank.com/profile/0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e))|
|||Fantom: `0x45b798384c236ef0d78311D98AcAEc222f8c6F54` ([FTMScan](https://ftmscan.com/address/0x45b798384c236ef0d78311D98AcAEc222f8c6F54), [Fantom Safe](https://safe.fantom.network/#/safes/0x45b798384c236ef0d78311D98AcAEc222f8c6F54/), [Zapper](https://zapper.fi/account/0x45b798384c236ef0d78311D98AcAEc222f8c6F54), [DeBank](https://debank.com/profile/0x45b798384c236ef0d78311D98AcAEc222f8c6F54))|
|`treasuryops.badgerdao.eth`|Treasury short-term holdings; beneficiary of DAO's fees and treasury's yield. Processes these incoming tokens into long-term holdings for the treasury vault.|Mainnet: `0x042B32Ac6b453485e357938bdC38e0340d4b9276` ([Etherscan](https://etherscan.io/address/0x042B32Ac6b453485e357938bdC38e0340d4b9276), [Gnosis Safe](https://gnosis-safe.io/app/eth:0x042B32Ac6b453485e357938bdC38e0340d4b9276/), [Zapper](https://zapper.fi/account/0x042B32Ac6b453485e357938bdC38e0340d4b9276), [DeBank](https://debank.com/profile/0x042B32Ac6b453485e357938bdC38e0340d4b9276))|
|||Fantom: `0xf109c50684EFa12d4dfBF501eD4858F25A4300B3` ([FTMScan](https://ftmscan.com/address/0xf109c50684EFa12d4dfBF501eD4858F25A4300B3), [Fantom Safe](https://safe.fantom.network/#/safes/0xf109c50684EFa12d4dfBF501eD4858F25A4300B3/), [Zapper](https://zapper.fi/account/0xf109c50684EFa12d4dfBF501eD4858F25A4300B3), [DeBank](https://debank.com/profile/0xf109c50684EFa12d4dfBF501eD4858F25A4300B3))|
|`treasuryvoter.badgerdao.eth`|Holder of all voting locked tokens and other influence assets. Used for gauge voting and potential involvement in the governance of other protocols if required.|Mainnet: `0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b` ([Etherscan](https://etherscan.io/address/0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b), [Gnosis Safe](https://gnosis-safe.io/app/eth:0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b/), [Zapper](https://zapper.fi/account/0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b), [DeBank](https://debank.com/profile/0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b))|
|`payments.badgerdao.eth`|Financial txs such as payments to contractors, contributors, expenses, bounties, advisors, etc.|Mainnet: `0x30a9c1D258F6c2D23005e6450E72bDD42C541105` ([Etherscan](https://etherscan.io/address/0x30a9c1D258F6c2D23005e6450E72bDD42C541105), [Gnosis Safe](https://gnosis-safe.io/app/eth:0x30a9c1D258F6c2D23005e6450E72bDD42C541105/), [Zapper](https://zapper.fi/account/0x30a9c1D258F6c2D23005e6450E72bDD42C541105), [DeBank](https://debank.com/profile/0x30a9c1D258F6c2D23005e6450E72bDD42C541105))|
|`ibbtc.badgerdao.eth`|Holds assets acquired from ibBTC's yield which will be used to incentivize eBTC as per [BIP 100](https://forum.badger.finance/t/bip-100-allocation-of-unclaimed-ibbtc-rewards/6012).|Mainnet: `0xB76782B51BFf9C27bA69C77027e20Abd92Bcf3a8` ([Etherscan](https://etherscan.io/address/0xB76782B51BFf9C27bA69C77027e20Abd92Bcf3a8), [Gnosis Safe](https://gnosis-safe.io/app/eth:0xB76782B51BFf9C27bA69C77027e20Abd92Bcf3a8/), [Zapper](https://zapper.fi/account/0xB76782B51BFf9C27bA69C77027e20Abd92Bcf3a8), [DeBank](https://debank.com/profile/0xB76782B51BFf9C27bA69C77027e20Abd92Bcf3a8))|

## Techops Signers

The following is a list of all signers on `techops.badgerdao.eth`:

| Signer | Profiles | Address |
|-|-|-|
| petrovska | [GitHub](https://github.com/petrovska-petro) | `0x0a9af7FAba0d5DF7A8C881e1B9cd679ee07Af8A2` |
| dapp-whisperer | [GitHub](https://github.com/dapp-whisperer/) | `0x8938bf50d1a3736bdA413510688834540858dAEA` |
| ICEITH | [GitHub](https://github.com/ICEBADGER) | `0x5F0D1a3355a75C47324c857280043DdE27797bC0` |
| lipp | [Twitter](https://twitter.com/lipp_brian) | `0xaC7B5f4E631b7b5638B9b41d07f1eBED30753f16` |
| mrbasado | [GitHub](https://github.com/mrbasado) | `0xE78e3E1668D42FfCa767e22e57d7d249e02B5F0e` |
| saj | [GitHub](https://github.com/sajanrajdev) | `0xfA5bb45895Cb3C0aE5B1583Fe068f009A48F0187` |

## Treasury Signers

The following is a list of all Treasury Council members and therefore the signers on `treasuryvault.badgerdao.eth`, `treasuryops.badgerdao.eth` and `treasuryvoter.badgerdao.eth`:

| Signer | Profiles | Address |
|-|-|-|
| petrovska | [GitHub](https://github.com/petrovska-petro) | `0x0a9af7FAba0d5DF7A8C881e1B9cd679ee07Af8A2` |
| adcv | [Twitter](https://twitter.com/adcv_) | `0x2afc096981c2CFe3501bE4054160048718F6C0C8` |
| 1500$Badger | [Twitter](https://twitter.com/haal69k) | `0x66496eBB9d848C6A8F19612a6Dd10E09954532D0` |
| gosuto | [GitHub](https://github.com/gosuto-inzasheru/) | `0x6C6238309f4f36DFF9942e655A678bbd4EA3BC5d` |
| Po | [Forum](https://forum.badger.finance/u/mr_po/summary) | `0x9c8C8bcD625Ed2903823b0b60DeaB2D70B92aFd9` |
| juanbug | [Twitter](https://twitter.com/juanbugeth) | `0xB8Dcad009E533066F12e408075E10E3a30F1f15A` |
| dapp-whisperer | [GitHub](https://github.com/dapp-whisperer/) | `0xaF94D299a73c4545ff702E79D16d9fb1AB5BDAbF` |
| saj | [GitHub](https://github.com/sajanrajdev) | `0xD10617AE4Da733d79eF0371aa44cd7fa74C41f6B` |
| Freddy the Filosopher | [Forum](https://forum.badger.finance/u/freddythefilosopher/summary) | `0xaFD01c6161729aa857404763c9577498327c6Aee` |
