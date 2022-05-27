from great_ape_safe import GreatApeSafe
from helpers.addresses import get_registry as registry
from brownie import chain

contract_registry = registry()
chain_safe = GreatApeSafe(contract_registry.badger_wallets.techops_multisig)
chain_safe.init_badger()

FANTOM_VAULTS = [
  [
    '0xFce6e3115D84c94df98BD286C1C67279dc021361',
    'v1',
    'name=%F0%9F%91%BB%20BOO/xBOO,protocol=Solidex,behavior=Ecosystem',
    0
  ],
  [
    '0xB6D63A4e5Ca740e96C26AdAbcAc73BE78Ee39Dc5',
    'v1',
    'name=WBTC/renBTC,protocol=Solidex,behavior=Compounder',
    2
  ],
  [
    '0x7cc6049a125388B51c530e51727A87aE101f6417',
    'v1',
    'name=WFTM/SEX,protocol=Solidex,behavior=Ecosystem Helper',
    0
  ],
  [
    '0xC7cBF5a24caBA375C09cc824481F5508c644dF28',
    'v1',
    'name=SOLID/SOLIDsex,protocol=Solidex,behavior=Ecosystem Helper',
    0
  ],
  [
    '0xd9770deC6fdA576450e66f0c441B6b8755F7184A',
    'v1',
    'name=WEVE/USDC,protocol=Solidex,behavior=Compounder',
    2
  ],
  [
    '0x4145a9B8B7bdC76F14e65c26f9c71e23B9069b25',
    'v1',
    'name=WFTM/CRV,protocol=Solidex,behavior=Bitcoin Rewards',
    2
  ],
  [
    '0x1AaF7f8154704D80E2380B3DbC967FD0486016e0',
    'v1',
    'name=USDC/MIM,protocol=Solidex,behavior=Bitcoin Rewards',
    2
  ],
  [
    '0x9a28eeFB2c5F8311f37c39314D78Be85C54B5da6',
    'v1',
    'name=WFTM/renBTC,protocol=Solidex,behavior=Bitcoin Rewards',
    2
  ],
  [
    '0x02330E37fcc7C27eB4632b3E31b951fDE5126c48',
    'v1',
    'name=GEIST/g3CRV,protocol=Solidex,behavior=Bitcoin Rewards',
    0
  ],
  [
    '0x60c5A975Bd0511e45D4C9Ae5592c8CA412BE2310',
    'v1',
    'name=%F0%9F%91%BB%20WFTM/CRV,protocol=Solidex,behavior=Ecosystem',
    0
  ],
  [
    '0x561f4dBaFA71ad05694C7ea1b894b9D99f684281',
    'v1',
    'name=%F0%9F%91%BB%20USDC/MIM,protocol=Solidex,behavior=Ecosystem',
    0
  ],
  [
    '0x77e803F7d0B6d85731F68CfE1f1CA4c48de105F4',
    'v1',
    'name=%F0%9F%91%BB%20WFTM/SCREAM,protocol=Solidex,behavior=Ecosystem',
    0
  ],
  [
    '0x609A51e13fd0896c0c02f0B642756533b29f36Ab',
    'v1',
    'name=%F0%9F%91%BB%20WFTM/renBTC,protocol=Solidex,behavior=Ecosystem',
    0
  ],
  [
    '0x3f96f8cA67AcDE9041AD62125C5a4D062b07872c',
    'v1',
    'name=%F0%9F%91%BB%20WFTM/TOMB,protocol=Solidex,behavior=Ecosystem',
    0
  ],
  [
    '0x96d4dBdc91Bef716eb407e415c9987a9fAfb8906',
    'v1.5',
    'name=bveOXD,protocol=0xDAO,behavior=None',
    2
  ],
  [
    '0xa8bD8655A0dCABE76913D821Ab437562276b3B59',
    'v1.5',
    'name=boxSOLID,protocol=0xDAO,behavior=Ecosystem Helper',
    2
  ],
  [
    '0xbF2F3a9ba42A00CA5B18842D8eB1954120e4a2A9',
    'v1.5',
    'name=bveOXD/OXD,protocol=0xDAO,behavior=Ecosystem Helper',
    2
  ],
  [
    '0xcd1e62b390373fcFeA87Dd06E2497Fdc907935fA',
    'v1.5',
    'name=USDC/DEI,protocol=0xDAO,behavior=Ecosystem',
    2
  ]
]

def get_chain_vaults():
  if chain.id == 250:
    return FANTOM_VAULTS

def register_vaults():
  for vault in get_chain_vaults():
    print(vault)
    chain_safe.badger.promote_vault(vault[0], vault[1], vault[2], vault[3])
  
  chain_safe.post_safe_tx()
