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
    3
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
    3
  ],
  [
    '0x4145a9B8B7bdC76F14e65c26f9c71e23B9069b25',
    'v1',
    'name=WFTM/CRV,protocol=Solidex,behavior=Bitcoin Rewards',
    3
  ],
  [
    '0x1AaF7f8154704D80E2380B3DbC967FD0486016e0',
    'v1',
    'name=USDC/MIM,protocol=Solidex,behavior=Bitcoin Rewards',
    3
  ],
  [
    '0x9a28eeFB2c5F8311f37c39314D78Be85C54B5da6',
    'v1',
    'name=WFTM/renBTC,protocol=Solidex,behavior=Bitcoin Rewards',
    3
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
    3
  ],
  [
    '0xa8bD8655A0dCABE76913D821Ab437562276b3B59',
    'v1.5',
    'name=boxSOLID,protocol=0xDAO,behavior=Ecosystem Helper',
    3
  ],
  [
    '0xbF2F3a9ba42A00CA5B18842D8eB1954120e4a2A9',
    'v1.5',
    'name=bveOXD/OXD,protocol=0xDAO,behavior=Ecosystem Helper',
    3
  ],
  [
    '0xcd1e62b390373fcFeA87Dd06E2497Fdc907935fA',
    'v1.5',
    'name=USDC/DEI,protocol=0xDAO,behavior=Ecosystem',
    3
  ]
]

ARBITRUM_VAULTS = [
  [
    '0xe774D1FB3133b037AA17D39165b8F45f444f632d',
    'v1',
    'name=wETH/Sushi,protocol=Sushiswap,behavior=None',
    3
  ],
  [
    '0xFc13209cAfE8fb3bb5fbD929eC9F11a39e8Ac041',
    'v1',
    'name=wBTC/wETH,protocol=Sushiswap,behavior=None',
    3
  ],
  [
    '0xBA418CDdd91111F5c1D1Ac2777Fa8CEa28D71843',
    'v1',
    'name=renBTC/wBTC,protocol=Curve,behavior=None',
    3
  ],
  [
    '0x4591890225394BF66044347653e112621AF7DDeb',
    'v1',
    'name=Tricrypto,protocol=Curve,behavior=None',
    3
  ],
  [
    '0x0c2153e8aE4DB8233c61717cDC4c75630E952561',
    'v1',
    'name=Swapr/wETH,protocol=Swapr,behavior=None',
    3
  ],
  [
    '0xaf9aB64F568149361ab670372b16661f4380e80B',
    'v1',
    'name=wBTC/wETH,protocol=Swapr,behavior=None',
    3
  ],
  [
    '0xE9C12F06F8AFFD8719263FE4a81671453220389c',
    'v1',
    'name=Badger/wETH,protocol=Swapr,behavior=None',
    3
  ],
  [
    '0x60129B2b762952Dfe8b21f40ee8aa3B2A4623546',
    'v1',
    'name=ibBTC/wETH,protocol=Swapr,behavior=None',
    3
  ]
]

POLYGON_VAULTS = [
  [
    '0xEa8567d84E3e54B32176418B4e0C736b56378961',
    'v1',
    'name=wBTC/ibBTC,protocol=Sushiswap,behavior=None',
    3
  ],
  [
    '0x6B2d4c4bb50274c5D4986Ff678cC971c0260E967',
    'v1',
    'name=wBTC/USDC,protocol=Quickswap,behavior=None',
    3
  ],
  [
    '0x7B6bfB88904e4B3A6d239d5Ed8adF557B22C10FC',
    'v1',
    'name=amWBTC/renBTC,protocol=Curve,behavior=None',
    3
  ]
]

def get_chain_vaults():
  if chain.id == 250:
    return FANTOM_VAULTS
  elif chain.id == 42161:
    return ARBITRUM_VAULTS
  elif chain.id == 137:
    return ARBITRUM_VAULTS

def register_vaults():
  for vault in get_chain_vaults():
    print(vault)
    chain_safe.badger.promote_vault(vault[0], vault[1], vault[2], vault[3])
  
  chain_safe.post_safe_tx()
