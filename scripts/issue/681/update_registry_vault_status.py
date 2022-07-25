from great_ape_safe import GreatApeSafe
from helpers.addresses import get_registry as registry
from brownie import chain

contract_registry = registry()
chain_safe = GreatApeSafe(contract_registry.badger_wallets.techops_multisig)
chain_safe.init_badger()

# Deprecating everything on Polygon except for bveOXD LP and bveOXD
FANTOM_VAULTS_DEMOTE = [
  [
    '0xB6D63A4e5Ca740e96C26AdAbcAc73BE78Ee39Dc5',
    'v1',
    'name=WBTC/renBTC,protocol=Solidex,behavior=Compounder',
    0
  ],
  [
    '0xd9770deC6fdA576450e66f0c441B6b8755F7184A',
    'v1',
    'name=WEVE/USDC,protocol=Solidex,behavior=Compounder',
    0
  ],
  [
    '0x4145a9B8B7bdC76F14e65c26f9c71e23B9069b25',
    'v1',
    'name=WFTM/CRV,protocol=Solidex,behavior=Bitcoin Rewards',
    0
  ],
  [
    '0x1AaF7f8154704D80E2380B3DbC967FD0486016e0',
    'v1',
    'name=USDC/MIM,protocol=Solidex,behavior=Bitcoin Rewards',
    0
  ],
  [
    '0x9a28eeFB2c5F8311f37c39314D78Be85C54B5da6',
    'v1',
    'name=WFTM/renBTC,protocol=Solidex,behavior=Bitcoin Rewards',
    0
  ],
  [
    '0xa8bD8655A0dCABE76913D821Ab437562276b3B59',
    'v1.5',
    'name=boxSOLID,protocol=0xDAO,behavior=Ecosystem Helper',
    0
  ],
  [
    '0xcd1e62b390373fcFeA87Dd06E2497Fdc907935fA',
    'v1.5',
    'name=USDC/DEI,protocol=0xDAO,behavior=Ecosystem',
    0
  ]
]

# Adding Aura vaults as experimental (current status), when ready for guarded another transaction will be submitted for it
ETHEREUM_VAULTS_PROMOTE = [
  [
    contract_registry.sett_vaults.bauraBal,
    'v1.5',
    'name=auraBAL,protocol=Aura,behavior=Ecosystem Helper',
    1
  ],
  [
    contract_registry.sett_vaults.bBB_a_USD,
    'v1.5',
    'name=bb-a-USD,protocol=Aura,behavior=Ecosystem Helper',
    1
  ],
  [
    contract_registry.sett_vaults.b33auraBAL_33graviAURA_33WETH,
    'v1.5',
    'name=graviAURA/auraBAL/WETH,protocol=Aura,behavior=None',
    1
  ],
  [
    contract_registry.sett_vaults.b40WBTC_40DIGG_20graviAURA,
    'v1.5',
    'name=graviAURA/DIGG/WBTC,protocol=Aura,behavior=None',
    1
  ],
  [
    contract_registry.sett_vaults.b80BADGER_20WBTC,
    'v1.5',
    'name=BADGER/WBTC,protocol=Aura,behavior=None',
    1
  ],
  [
    contract_registry.sett_vaults.graviAURA,
    'v1.5',
    'name=graviAURA,protocol=Aura,behavior=None',
    3
  ],
]

ETHEREUM_VAULTS_DEMOTE = [
  [
    '0x88128580ACdD9c04Ce47AFcE196875747bF2A9f6',
    'v1',
    'name=wBTC/Digg,protocol=Sushiswap,behavior=None',
    0
  ],
  [
    '0x7e7E112A68d8D2E221E11047a72fFC1065c38e1a',
    'v1',
    'name=Digg,protocol=Badger,behavior=None',
    0
  ],
]

def get_chain_promote_vaults():
  if chain.id == 1:
    return ETHEREUM_VAULTS_PROMOTE
  elif chain.id == 250:
    return []

def get_chain_demote_vaults():
  if chain.id == 1:
    return ETHEREUM_VAULTS_DEMOTE
  elif chain.id == 250:
    return FANTOM_VAULTS_DEMOTE

def main():
    # Promte vaults
    for vault in get_chain_promote_vaults():
        print(vault)
        chain_safe.badger.promote_vault(vault[0], vault[1], vault[2], vault[3])

    # Demote vaults
    for vault in get_chain_demote_vaults():
        print(vault)
        chain_safe.badger.demote_vault(vault[0], vault[3])

    chain_safe.post_safe_tx()