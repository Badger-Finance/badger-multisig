from great_ape_safe import GreatApeSafe
from helpers.addresses import get_registry as registry
from brownie import chain

contract_registry = registry()
chain_safe = GreatApeSafe(contract_registry.badger_wallets.techops_multisig)
chain_safe.init_badger()

FANTOM_VAULTS = [
    [
        "0xFce6e3115D84c94df98BD286C1C67279dc021361",
        "v1",
        "name=%F0%9F%91%BB%20BOO/xBOO,protocol=Solidex,behavior=Ecosystem",
        0,
    ],
    [
        "0xB6D63A4e5Ca740e96C26AdAbcAc73BE78Ee39Dc5",
        "v1",
        "name=WBTC/renBTC,protocol=Solidex,behavior=Compounder",
        3,
    ],
    [
        "0x7cc6049a125388B51c530e51727A87aE101f6417",
        "v1",
        "name=WFTM/SEX,protocol=Solidex,behavior=Ecosystem Helper",
        0,
    ],
    [
        "0xC7cBF5a24caBA375C09cc824481F5508c644dF28",
        "v1",
        "name=SOLID/SOLIDsex,protocol=Solidex,behavior=Ecosystem Helper",
        0,
    ],
    [
        "0xd9770deC6fdA576450e66f0c441B6b8755F7184A",
        "v1",
        "name=WEVE/USDC,protocol=Solidex,behavior=Compounder",
        3,
    ],
    [
        "0x4145a9B8B7bdC76F14e65c26f9c71e23B9069b25",
        "v1",
        "name=WFTM/CRV,protocol=Solidex,behavior=Bitcoin Rewards",
        3,
    ],
    [
        "0x1AaF7f8154704D80E2380B3DbC967FD0486016e0",
        "v1",
        "name=USDC/MIM,protocol=Solidex,behavior=Bitcoin Rewards",
        3,
    ],
    [
        "0x9a28eeFB2c5F8311f37c39314D78Be85C54B5da6",
        "v1",
        "name=WFTM/renBTC,protocol=Solidex,behavior=Bitcoin Rewards",
        3,
    ],
    [
        "0x02330E37fcc7C27eB4632b3E31b951fDE5126c48",
        "v1",
        "name=GEIST/g3CRV,protocol=Solidex,behavior=Bitcoin Rewards",
        0,
    ],
    [
        "0x60c5A975Bd0511e45D4C9Ae5592c8CA412BE2310",
        "v1",
        "name=%F0%9F%91%BB%20WFTM/CRV,protocol=Solidex,behavior=Ecosystem",
        0,
    ],
    [
        "0x561f4dBaFA71ad05694C7ea1b894b9D99f684281",
        "v1",
        "name=%F0%9F%91%BB%20USDC/MIM,protocol=Solidex,behavior=Ecosystem",
        0,
    ],
    [
        "0x77e803F7d0B6d85731F68CfE1f1CA4c48de105F4",
        "v1",
        "name=%F0%9F%91%BB%20WFTM/SCREAM,protocol=Solidex,behavior=Ecosystem",
        0,
    ],
    [
        "0x609A51e13fd0896c0c02f0B642756533b29f36Ab",
        "v1",
        "name=%F0%9F%91%BB%20WFTM/renBTC,protocol=Solidex,behavior=Ecosystem",
        0,
    ],
    [
        "0x3f96f8cA67AcDE9041AD62125C5a4D062b07872c",
        "v1",
        "name=%F0%9F%91%BB%20WFTM/TOMB,protocol=Solidex,behavior=Ecosystem",
        0,
    ],
    [
        "0x96d4dBdc91Bef716eb407e415c9987a9fAfb8906",
        "v1.5",
        "name=bveOXD,protocol=0xDAO,behavior=None",
        3,
    ],
    [
        "0xa8bD8655A0dCABE76913D821Ab437562276b3B59",
        "v1.5",
        "name=boxSOLID,protocol=0xDAO,behavior=Ecosystem Helper",
        3,
    ],
    [
        "0xbF2F3a9ba42A00CA5B18842D8eB1954120e4a2A9",
        "v1.5",
        "name=bveOXD/OXD,protocol=0xDAO,behavior=Ecosystem Helper",
        3,
    ],
    [
        "0xcd1e62b390373fcFeA87Dd06E2497Fdc907935fA",
        "v1.5",
        "name=USDC/DEI,protocol=0xDAO,behavior=Ecosystem",
        3,
    ],
]

ARBITRUM_VAULTS = [
    [
        "0xe774D1FB3133b037AA17D39165b8F45f444f632d",
        "v1",
        "name=wETH/Sushi,protocol=Sushiswap,behavior=None",
        3,
    ],
    [
        "0xFc13209cAfE8fb3bb5fbD929eC9F11a39e8Ac041",
        "v1",
        "name=wBTC/wETH,protocol=Sushiswap,behavior=None",
        3,
    ],
    [
        "0xBA418CDdd91111F5c1D1Ac2777Fa8CEa28D71843",
        "v1",
        "name=renBTC/wBTC,protocol=Curve,behavior=None",
        3,
    ],
    [
        "0x4591890225394BF66044347653e112621AF7DDeb",
        "v1",
        "name=Tricrypto,protocol=Curve,behavior=None",
        3,
    ],
    [
        "0x0c2153e8aE4DB8233c61717cDC4c75630E952561",
        "v1",
        "name=Swapr/wETH,protocol=Swapr,behavior=None",
        3,
    ],
    [
        "0xaf9aB64F568149361ab670372b16661f4380e80B",
        "v1",
        "name=wBTC/wETH,protocol=Swapr,behavior=None",
        3,
    ],
    [
        "0xE9C12F06F8AFFD8719263FE4a81671453220389c",
        "v1",
        "name=Badger/wETH,protocol=Swapr,behavior=None",
        3,
    ],
    [
        "0x60129B2b762952Dfe8b21f40ee8aa3B2A4623546",
        "v1",
        "name=ibBTC/wETH,protocol=Swapr,behavior=None",
        3,
    ],
]

POLYGON_VAULTS = [
    [
        "0xEa8567d84E3e54B32176418B4e0C736b56378961",
        "v1",
        "name=wBTC/ibBTC,protocol=Sushiswap,behavior=None",
        3,
    ],
    [
        "0x6B2d4c4bb50274c5D4986Ff678cC971c0260E967",
        "v1",
        "name=wBTC/USDC,protocol=Quickswap,behavior=None",
        3,
    ],
    [
        "0x7B6bfB88904e4B3A6d239d5Ed8adF557B22C10FC",
        "v1",
        "name=amWBTC/renBTC,protocol=Curve,behavior=None",
        3,
    ],
]

ETHEREUM_VAULTS = [
    [
        "0xd04c48A53c111300aD41190D63681ed3dAd998eC",
        "v1",
        "name=renBTC/wBTC/sBTC,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0x6dEf55d2e18486B9dDfaA075bc4e4EE0B28c1545",
        "v1",
        "name=renBTC/wBTC,protocol=Convex,behavior=None",
        3,
    ],
    [
        "0xb9D076fDe463dbc9f915E5392F807315Bf940334",
        "v1",
        "name=tBTC/sBTC,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0xAf5A1DECfa95BAF63E0084a35c62592B774A2A87",
        "v1",
        "name=renBTC/wBTC,protocol=Curve,behavior=None",
        0,
    ],
    [
        "0x235c9e24D3FB2FAFd58a2E49D454Fdcd2DBf7FF1",
        "v1",
        "name=wBTC/Badger,protocol=Uniswap,behavior=None",
        0,
    ],
    [
        "0xC17078FDd324CC473F8175Dc5290fae5f2E84714",
        "v1",
        "name=wBTC/Digg,protocol=Uniswap,behavior=None",
        0,
    ],
    [
        "0x758A43EE2BFf8230eeb784879CdcFF4828F2544D",
        "v1",
        "name=wBTC/wETH,protocol=Sushiswap,behavior=None",
        3,
    ],
    [
        "0x1862A18181346EBd9EdAf800804f89190DeF24a5",
        "v1",
        "name=wBTC/Badger,protocol=Sushiswap,behavior=None",
        3,
    ],
    [
        "0x88128580ACdD9c04Ce47AFcE196875747bF2A9f6",
        "v1",
        "name=wBTC/Digg,protocol=Sushiswap,behavior=None",
        3,
    ],
    [
        "0x7e7E112A68d8D2E221E11047a72fFC1065c38e1a",
        "v1",
        "name=Digg,protocol=Badger,behavior=None",
        3,
    ],
    [
        "0x19D97D8fA813EE2f51aD4B4e04EA08bAf4DFfC28",
        "v1",
        "name=Badger,protocol=Badger,behavior=None",
        0,
    ],
    [
        "0x4b92d19c11435614CD49Af1b589001b7c08cD4D5",
        "v1",
        "name=wBTC,protocol=Yearn,behavior=None",
        3,
    ],
    [
        "0x8a8FFec8f4A0C8c9585Da95D9D97e8Cd6de273DE",
        "v1",
        "name=wBTC/ibBTC,protocol=Sushiswap,behavior=None",
        0,
    ],
    [
        "0x8c76970747afd5398e958bDfadA4cf0B9FcA16c4",
        "v1",
        "name=hBTC,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0x55912D0Cf83B75c492E761932ABc4DB4a5CB1b17",
        "v1",
        "name=pBTC,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0xf349c0faA80fC1870306Ac093f75934078e28991",
        "v1",
        "name=oBTC,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0x5Dce29e92b1b939F8E8C60DcF15BDE82A85be4a9",
        "v1",
        "name=bBTC,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0xBE08Ef12e4a553666291E9fFC24fCCFd354F2Dd2",
        "v1",
        "name=Tricrypto,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0x2B5455aac8d64C14786c3a29858E43b5945819C0",
        "v1",
        "name=cvxCRV,protocol=Convex,behavior=Ecosystem Helper",
        3,
    ],
    [
        "0x53C8E199eb2Cb7c01543C137078a038937a68E40",
        "v1",
        "name=CVX,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0x27E98fC7d05f54E544d16F58C194C2D7ba71e3B5",
        "v1",
        "name=Tricrypto2,protocol=Convex,behavior=None",
        3,
    ],
    [
        "0x599D92B453C010b1050d31C364f6ee17E819f193",
        "v1",
        "name=imBTC,protocol=mStable,behavior=None",
        0,
    ],
    [
        "0x26B8efa69603537AC8ab55768b6740b67664D518",
        "v1",
        "name=mhBTC,protocol=mStable,behavior=None",
        0,
    ],
    [
        "0xfd05D3C7fe2924020620A8bE4961bBaA747e6305",
        "v1",
        "name=bveCVX,protocol=Convex,behavior=None",
        3,
    ],
    [
        "0x937B8E917d0F36eDEBBA8E459C5FB16F3b315551",
        "v1",
        "name=CVX/bveCVX,protocol=Curve,behavior=None",
        3,
    ],
    [
        "0xaE96fF08771a109dc6650a1BdCa62F2d558E40af",
        "v1",
        "name=ibBTC/crvsBTC,protocol=Convex,behavior=None",
        3,
    ],
    [
        "0x19E4d89e0cB807ea21B8CEF02df5eAA99A110dA5",
        "v1",
        "name=MIM/3CRV,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0x15cBC4ac1e81c97667780fE6DAdeDd04a6EEB47B",
        "v1",
        "name=FRAX/3CRV,protocol=Convex,behavior=None",
        0,
    ],
    [
        "0x6aF7377b5009d7d154F36FE9e235aE1DA27Aea22",
        "v1",
        "name=remBadger,protocol=Badger,behavior=None",
        3,
    ],
    [
        "0xeC1c717A3b02582A4Aa2275260C583095536b613",
        "v1",
        "name=BADGER/WBTC,protocol=Convex,behavior=None",
        3,
    ],
]


def get_chain_vaults():
    if chain.id == 1:
        return ETHEREUM_VAULTS
    elif chain.id == 250:
        return FANTOM_VAULTS
    elif chain.id == 42161:
        return ARBITRUM_VAULTS
    elif chain.id == 137:
        return POLYGON_VAULTS


def register_vaults():
    for vault in get_chain_vaults():
        print(vault)
        chain_safe.badger.promote_vault(vault[0], vault[1], vault[2], vault[3])

    chain_safe.post_safe_tx()
