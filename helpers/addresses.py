import pandas as pd

from dotmap import DotMap
from web3 import Web3
import json

ADDRESSES_ETH = {
    "zero": "0x0000000000000000000000000000000000000000",
    "treasury": "0x8dE82C4C968663a0284b01069DDE6EF231D0Ef9B",
    "governance_timelock": "0x21CF9b77F88Adf8F8C98d7E33Fe601DC57bC0893",
    "rewardsLogger" : "0x0A4F4e92C3334821EbB523324D09E321a6B0d8ec",
    "EmissionControl": "0x31825c0A6278b89338970e3eB979b05B27FAa263",
    "registry": "0xFda7eB6f8b7a9e9fCFd348042ae675d1d652454f",
    "keeperAccessControl": "0x711A339c002386f9db409cA55b6A35a604aB6cF6",
    "guardian": "0x6615e67b8B6b6375D38A0A3f937cd8c1a1e96386",
    "GatedMiniMeController": "0xdDB2dfad74F64F14bb1A1cbaB9C03bc0eed74493",
    "GlobalAccessControl": "0x9c58B0D88578cd75154Bdb7C8B013f7157bae35a",
    "badger_geyser": "0xBD9c69654B8F3E5978DFd138B00cB0Be29F28cCf",
    "drippers": {
        "rembadger_2022_q2": "0xD87F434fE6d5B349f4376d2daBA762b213E403c7",
    },
    "bribes_processor": "0xbeD8f323456578981952e33bBfbE80D23289246B",
    # the wallets listed here are looped over by scout and checked for all treasury tokens
    "badger_wallets": {
        "fees": "0x8dE82C4C968663a0284b01069DDE6EF231D0Ef9B",
        "team": "0xe4aa1d8aaf8a50422bc5c7310deb1262d1f6f657",
        "badgertree": "0x660802fc641b154aba66a62137e71f331b6d787a",
        "native_autocompounder": "0x5B60952481Eb42B66bdfFC3E049025AC5b91c127",
        "badgerhunt": "0x394dcfbcf25c5400fcc147ebd9970ed34a474543",
        "DAO_treasury": "0x4441776e6a5d61fa024a5117bfc26b953ad1f425",
        "rewards_escrow": "0x19d099670a21bc0a8211a89b84cedf59abb4377f",
        "dev_multisig": "0xB65cef03b9B89f99517643226d76e286ee999e77",
        "test_multisig_1": "0x55949f769d0af7453881435612561d109fff07b8",
        "test_multisig": "0x33909cb2633d4B298a72042Da5686B45E9385ed0",
        "test_multisig_v1_3": "0xb86f6c9e3158cC4C540219244b80722d6bd9B033",
        "techops_multisig": "0x86cbD0ce0c087b482782c181dA8d191De18C8275",
        "politician_multisig": "0x6F76C6A1059093E21D8B1C13C4e20D8335e2909F",
        "recovered_multisig": "0x9faA327AAF1b564B569Cb0Bc0FDAA87052e8d92c",
        "ops_multisig": "0xD4868d98849a58F743787c77738D808376210292",
        "ops_multisig_old": "0x576cD258835C529B54722F84Bb7d4170aA932C64",
        "treasury_ops_multisig": "0x042B32Ac6b453485e357938bdC38e0340d4b9276",
        "treasury_vault_multisig": "0xD0A7A8B98957b9CD3cFB9c0425AbE44551158e9e",
        "ibbtc_multisig": "0xB76782B51BFf9C27bA69C77027e20Abd92Bcf3a8",
        "bvecvx_voting_multisig": "0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b",
        "payments_multisig": "0x30a9c1D258F6c2D23005e6450E72bDD42C541105",
        "dfdBadgerShared": "0xCF7346A5E41b0821b80D5B3fdc385EEB6Dc59F44",
        "ops_deployer": "0xDA25ee226E534d868f0Dd8a459536b03fEE9079b",
        "ops_deployer2": "0xeE8b29AA52dD5fF2559da2C50b1887ADee257556",
        "ops_deployer3": "0x283C857BA940A61828d9F4c09e3fceE2e7aEF3f7",
        "ops_deployer4": "0xef42D748e09A2d9eF89238c053CE0B6f00236210",
        "ops_deployer5": "0xC6a902de22b10cb176460777ce6e7A12A6b6AE5a",
        "ops_deployer6": "0x96AC69183216074dd8CFA7A380e873380445EaDc",
        "ops_deployer7": "0x7140B5254d80154f9Fc5F86054efB210f3a1e2c6",
        "ops_deployer8": "0x9082b0dD7A72c328833e6461965C9E91Cf59a960",
        "ops_executor1": "0xcf4fF1e03830D692F52EB094c52A5A6A2181Ab3F",
        "ops_executor2": "0x8938bf50d1a3736bdA413510688834540858dAEA",
        "ops_executor3": "0xC69Fb085481bC8C4bfF99B924076656305D9a25D",
        "ops_executor4": "0xBB2281cA5B4d07263112604D1F182AD0Ab26a252",
        "ops_executor5": "0xcDAb3AcC1AD3870a93BB72377092B67e290D76f3",
        "ops_executor6": "0x66496eBB9d848C6A8F19612a6Dd10E09954532D0",
        "ops_executor7": "0xaaE2051c2f74920C6662EF5C9B0d602C40D36DF4",
        "ops_executor8": "0x10C7a2ca16116E5C998Bfa3BC9CEF464475B18ff",
        # "ops_executor9": "0x69874C84a30A3742cC2b624238CfEEa24CF5eF82",
        "ops_executor10": "0xaF94D299a73c4545ff702E79D16d9fb1AB5BDAbF",
        # "ops_executor11": "0x54cf9df9dcd78e470ab7cb892d7bfbe114c025fc",
        "ops_guardian": "0x29F7F8896Fb913CF7f9949C623F896a154727919",
        "ops_keeper": "0x872213E29C85d7e30F1C8202FC47eD1Ec124BB1D",
        "OLD_root-validator": "0x626f69162ea1556a75dd4443d87d2fe38dd25901",
        "ops_root-validator-new": "0x1318d5c0C24830D86Cc27Db13Ced0CED31412438",
        "ops_cycle_bot": "0x68de9E2b015904530593426d934CE608e117Fa7A",
        "ops_botsquad": "0xF8dbb94608E72A3C4cEeAB4ad495ac51210a341e",
        "ops_botsquad_cycle0": "0x1a6D6D120a7e3F71B084b4023a518c72F1a93EE9",
        "ops_earner": "0x46099Ffa86aAeC689D11F5D5130044Ff7082C2AD",
        "ops_harvester": "0x73433896620E71f7b1C72405b8D2898e951Ca4d5",
        "ops_external_harvester": "0x64E2286148Fbeba8BEb4613Ede74bAc7646B2A2B",
        "digg_treasury": "0x5A54Ca44e8F5A1A695f8621f15Bfa159a140bB61",
        "uniswap_rewards": "0x0c79406977314847a9545b11783635432d7fe019",
        "defiDollar_fees": "0x5b5cf8620292249669e1dcc73b753d01543d6ac7",
        "delegate": "0x14f83ff95d4ec5e8812ddf42da1232b0ba1015e6",
        "devProxyAdmin": "0x20Dce41Acca85E8222D6861Aa6D23B6C941777bF",
        "devUngatedProxyAdmin": "0x9215cBDCDe25629d0e3D69ee5562d1b444Cf69F9",
        "testProxyAdmin": "0xB10b3Af646Afadd9C62D663dd5d226B15C25CdFA",
        "techOpsProxyAdmin": "0x7D0398D7D7432c47Dffc942Cd097B9eA3d88C385",
        "opsProxyAdmin_old": "0x4599F2913a3db4E73aA77A304cCC21516dd7270D",
        "badgerHunt": "0x394DCfbCf25C5400fcC147EbD9970eD34A474543",
        "rewardsEscrow": "0xBE838aE7f6Ba97e7Eb545a3f43eE96FfBb3184DC",
        "_deprecated": {
            "ops_deployer6": "0x7c1D678685B9d2F65F1909b9f2E544786807d46C",
        },
    },
    # scout stores prices for all tokens here, either from coingecko or
    # interpolation. any token here that does not have a coingeco price must be
    # included in sett_vaults, lp_tokens or crvpools or one of the crv_ lists
    # in order to have its price calculated and not break scout.
    "treasury_tokens": {
        "FARM": "0xa0246c9032bC3A600820415aE600c6388619A14D",
        "BADGER": "0x3472A5A71965499acd81997a54BBA8D852C6E53d",
        "ibBTC": "0xc4E15973E6fF2A35cC804c2CF9D2a1b817a8b40F",
        "wibBTC": "0x8751D4196027d4e6DA63716fA7786B5174F04C15",
        "DIGG": "0x798D1bE841a82a273720CE31c822C61a67a601C3",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "aUSDC": "0xBcca60bB61934080951369a648Fb03DF4F96263C",
        "aUSDT": "0x3Ed3B47Dd13EC9a98b44e6204A523E766B225811",
        "aFEI": "0x683923dB55Fead99A79Fa01A27EeC3cB19679cC3",
        "cUSDC": "0x39aa39c021dfbae8fac545936693ac917d5e7563",
        "cDAI": "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643",
        "cETH": "0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5",
        "DUSD": "0x5BC25f649fc4e26069dDF4cF4010F9f706c23831",
        "alUSD": "0xBC6DA0FE9aD5f3b0d58160288917AA56653660E9",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "MIM": "0x99D8a9C45b2ecA8864373A26D1459e3Dff1e17F3",
        "FRAX": "0x853d955aCEf822Db058eb8505911ED77F175b99e",
        "FEI": "0x956F47F50A910163D8BF957Cf5846D573E7f87CA",
        "DFD": "0x20c36f062a31865bED8a5B1e512D9a1A20AA333A",
        "CRV": "0xD533a949740bb3306d119CC777fa900bA034cd52",
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "renBTC": "0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D",
        "sBTC": "0xfE18be6b3Bd88A2D2A7f928d00292E7a9963CfC6",
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "SUSHI": "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2",
        "GTC": "0xDe30da39c46104798bB5aA3fe8B9e0e1F348163F",
        "bDIGG": "0x7e7E112A68d8D2E221E11047a72fFC1065c38e1a",
        "bBADGER": "0x19D97D8fA813EE2f51aD4B4e04EA08bAf4DFfC28",
        "xSUSHI": "0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272",
        "COMP": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
        "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "stkAAVE": "0x4da27a545c0c5B758a6BA100e3a049001de870f5",
        "SPELL": "0x090185f2135308bad17527004364ebcc2d37e5f6",
        "ALCX": "0xdbdb4d16eda451d0503b854cf79d55697f90c8df",
        "FXS": "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0",
        "crvRenBTC": "0x49849C98ae39Fff122806C06791Fa73784FB3675",
        "crvSBTC": "0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3",
        "crvTBTC": "0x64eda51d3Ad40D56b9dFc5554E06F94e1Dd786Fd",
        "slpWbtcEth": "0xceff51756c56ceffca006cd410b03ffc46dd3a58",
        "slpWbtcBadger": "0x110492b31c59716ac47337e616804e3e3adc0b4a",
        "uniWbtcBadger": "0xcd7989894bc033581532d2cd88da5db0a4b12859",
        "uniWbtcDigg": "0xe86204c4eddd2f70ee00ead6805f917671f56c52",
        "slpWbtcDigg": "0x9a13867048e01c663ce8ce2fe0cdae69ff9f35e3",
        "slpWbtcibBTC": "0x18d98D452072Ac2EB7b74ce3DB723374360539f1",
        "slpEthBBadger": "0x0a54d4b378c8dbfc7bc93be50c85debafdb87439",
        "slpEthBDigg": "0xf9440fedc72a0b8030861dcdac39a75b544e7a3c",
        "crvHBTC": "0xb19059ebb43466C323583928285a49f558E572Fd",
        "crvBBTC": "0x410e3E86ef427e30B9235497143881f717d93c2A",
        "crvOBTC": "0x2fE94ea3d5d4a175184081439753DE15AeF9d614",
        "crvPBTC": "0xDE5331AC4B3630f94853Ff322B66407e0D6331E8",
        "crvIbBTC": "0xFbdCA68601f835b27790D98bbb8eC7f05FDEaA9B",
        "crvTricrypto": "0xcA3d75aC011BF5aD07a98d02f18225F9bD9A6BDF",
        "crvTricrypto2": "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff",
        "crv3pool": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490",
        "crvMIM": "0x5a6A4D54456819380173272A5E8E9B9904BdF41B",
        "crvALUSD": "0x43b4FdFD4Ff969587185cDB6f0BD875c5Fc83f8c",
        "crvFRAX": "0xd632f22692FaC7611d2AA1C0D552930D43CAEd3B",
        "CVX": "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
        "cvxCRV": "0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7",
        "bcvxCRV": "0x2B5455aac8d64C14786c3a29858E43b5945819C0",
        "bCVX": "0x53c8e199eb2cb7c01543c137078a038937a68e40",
        "bveCVX-CVX-f": "0x04c90C198b2eFF55716079bc06d7CCc4aa4d7512",
        "bcrvRenBTC": "0x6dEf55d2e18486B9dDfaA075bc4e4EE0B28c1545",
        "bcrvSBTC": "0xd04c48A53c111300aD41190D63681ed3dAd998eC",
        "bcrvTBTC": "0xb9D076fDe463dbc9f915E5392F807315Bf940334",
        "bveCVX": "0xfd05D3C7fe2924020620A8bE4961bBaA747e6305",
        "yvWBTC": "0xA696a63cc78DfFa1a63E9E50587C197387FF6C7E",  ##TODO NO COINGECKO PRICE
        "aBADGER": "0x43298F9f91a4545dF64748e78a2c777c580573d6",
        "badgerWBTC_f": "0x137469B55D1f15651BA46A89D0588e97dD0B6562",
        "EURS": "0xdB25f211AB05b1c97D595516F45794528a807ad8",
        "crv3eur": "0xb9446c4Ef5EBE66268dA6700D26f96273DE3d571",
        "FTM": "0x4E15361FD6b4BB609Fa63C81A2be19d873717870",
        "BAL": "0xba100000625a3754423978a60c9317c58a424e3D",
    },
    # every slp token listed in treasury tokens above must also be listed here.
    # the lp_tokens in this list are processed by scount to determine holdings
    # and underlying value and set the price for the token in treasury_tokens
    # note that only univ2 style tokens should be listed here
    "lp_tokens": {
        "slpWbtcEth": "0xceff51756c56ceffca006cd410b03ffc46dd3a58",
        "slpWbtcBadger": "0x110492b31c59716ac47337e616804e3e3adc0b4a",
        "uniWbtcBadger": "0xcd7989894bc033581532d2cd88da5db0a4b12859",
        "uniWbtcDigg": "0xe86204c4eddd2f70ee00ead6805f917671f56c52",
        "slpWbtcDigg": "0x9a13867048e01c663ce8ce2fe0cdae69ff9f35e3",
        "slpEthBBadger": "0x0a54d4b378c8dbfc7bc93be50c85debafdb87439",
        "slpEthBDigg": "0xf9440fedc72a0b8030861dcdac39a75b544e7a3c",
        "slpWbtcIbBTC": "0x18d98D452072Ac2EB7b74ce3DB723374360539f1",
    },
    # every single asset curve pool listed in treasury tokens must also be
    # listed here.  this does not include tricrypto or other crypto like pools.
    # this list contains curve pools in which all of the underlying tokens have
    # basically the same value.
    # again every curve pool listed in treasury_tokens must be in this list, or
    # crv_crypto_pools below
    "crv_pools": {
        "crvRenBTC": "0x93054188d876f558f4a66B2EF1d97d16eDf0895B",
        "crvSBTC": "0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714",
        "crvTBTC": "0xC25099792E9349C7DD09759744ea681C7de2cb66",
        "crvHBTC": "0x4CA9b3063Ec5866A4B82E437059D2C43d1be596F",
        "crvBBTC": "0x071c661B4DeefB59E2a3DdB20Db036821eeE8F4b",
        "crvOBTC": "0xd81dA8D904b52208541Bade1bD6595D8a251F8dd",
        "crvPBTC": "0x7F55DDe206dbAD629C080068923b36fe9D6bDBeF",
        "crvIbBTC": "0xFbdCA68601f835b27790D98bbb8eC7f05FDEaA9B",
    },
    # pool addresses for curve pools that handle non-stable coins like tricypto
    "crv_3_pools": {
        "crvTricrypto2": "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46",
        "crvTricrypto": "0x80466c64868E1ab14a1Ddf27A676C3fcBE638Fe5",
    },
    "crv_stablecoin_pools": {
        "crv3pool": "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
    },
    "crv_meta_pools": {
        "crvMIM": "0x5a6A4D54456819380173272A5E8E9B9904BdF41B",
        "crvALUSD": "0x43b4FdFD4Ff969587185cDB6f0BD875c5Fc83f8c",
        "crvFRAX": "0xd632f22692FaC7611d2AA1C0D552930D43CAEd3B",
        "bveCVX-CVX-f": "0x04c90C198b2eFF55716079bc06d7CCc4aa4d7512",
    },
    "crv_factory_pools": {
        "badgerWBTC_f": "0x50f3752289e1456BfA505afd37B241bca23e685d",
        "t_eth_f": "0x752eBeb79963cf0732E9c0fec72a49FD1DEfAEAC",
        "cvx_eth_f": "0xB576491F1E6e5E62f1d8F26062Ee822B40B0E0d4",
    },
    # mStable want tokens
    "mstable_vaults": {
        "imBTC": "0x17d8CBB6Bce8cEE970a4027d1198F6700A7a6c24",
        "FpMbtcHbtc": "0x48c59199Da51B7E30Ea200a74Ea07974e62C4bA7",
    },
    "sett_vaults": {
        "bBADGER": "0x19D97D8fA813EE2f51aD4B4e04EA08bAf4DFfC28",
        "bDIGG": "0x7e7E112A68d8D2E221E11047a72fFC1065c38e1a",
        "bcrvRenBTC": "0x6dEf55d2e18486B9dDfaA075bc4e4EE0B28c1545",
        "bcrvSBTC": "0xd04c48A53c111300aD41190D63681ed3dAd998eC",
        "bcrvTBTC": "0xb9D076fDe463dbc9f915E5392F807315Bf940334",
        "bharvestcrvRenBTC": "0xAf5A1DECfa95BAF63E0084a35c62592B774A2A87",
        "buniWbtcBadger": "0x235c9e24D3FB2FAFd58a2E49D454Fdcd2DBf7FF1",
        "bslpWbtcBadger": "0x1862A18181346EBd9EdAf800804f89190DeF24a5",
        "bslpWbtcibBTC": "0x8a8FFec8f4A0C8c9585Da95D9D97e8Cd6de273DE",
        "buniWbtcDigg": "0xC17078FDd324CC473F8175Dc5290fae5f2E84714",
        "bslpWbtcDigg": "0x88128580ACdD9c04Ce47AFcE196875747bF2A9f6",
        "bslpWbtcEth": "0x758A43EE2BFf8230eeb784879CdcFF4828F2544D",
        "bcrvHBTC": "0x8c76970747afd5398e958bdfada4cf0b9fca16c4",
        "bcrvPBTC": "0x55912d0cf83b75c492e761932abc4db4a5cb1b17",
        "bcrvOBTC": "0xf349c0faa80fc1870306ac093f75934078e28991",
        "bcrvBBTC": "0x5dce29e92b1b939f8e8c60dcf15bde82a85be4a9",
        "bcrvIbBTC": "0xaE96fF08771a109dc6650a1BdCa62F2d558E40af",
        "bcrvTricrypto": "0xBE08Ef12e4a553666291E9fFC24fCCFd354F2Dd2",
        "bcrvTricrypto2": "0x27E98fC7d05f54E544d16F58C194C2D7ba71e3B5",
        "bcvxCRV": "0x2B5455aac8d64C14786c3a29858E43b5945819C0",
        "bCVX": "0x53c8e199eb2cb7c01543c137078a038937a68e40",
        # "bbCVX": "0xE143aA25Eec81B4Fc952b38b6Bca8D2395481377",
        "bveCVX": "0xfd05D3C7fe2924020620A8bE4961bBaA747e6305",
        "bimBTC": "0x599D92B453C010b1050d31C364f6ee17E819f193",
        "bFpMbtcHbtc": "0x26B8efa69603537AC8ab55768b6740b67664D518",
        "bbveCVX-CVX-f": "0x937B8E917d0F36eDEBBA8E459C5FB16F3b315551",
        "remBADGER": "0x6aF7377b5009d7d154F36FE9e235aE1DA27Aea22",
        "remDIGG": "0x99F39D495C6A5237f43602f3Ab5F49786E46c9B0",
        "bcrvBadger": "0xeC1c717A3b02582A4Aa2275260C583095536b613",
    },
    "strategies": {
        "native.badger": "0x75b8E21BD623012Efb3b69E1B562465A68944eE6",
        "native.renCrv": "0x61e16b46F74aEd8f9c2Ec6CB2dCb2258Bdfc7071",
        "native.sbtcCrv": "0xCce0D2d1Eb2310F7e67e128bcFE3CE870A3D3a3d",
        "native.tbtcCrv": "0xAB73Ec65a1Ef5a2e5b56D5d6F36Bee4B2A1D3FFb",
        "native.uniBadgerWbtc": "0x95826C65EB1f2d2F0EDBb7EcB176563B61C60bBf",
        "harvest.renCrv": "0xaaE82E3c89e15E6F26F60724f115d5012363e030",
        "native.sushiWbtcEth": "0x7A56d65254705B4Def63c68488C0182968C452ce",
        "native.sushiBadgerWbtc": "0x3a494D79AA78118795daad8AeFF5825C6c8dF7F1",
        "native.digg": "0x4a8651F2edD68850B944AD93f2c67af817F39F62",
        "native.uniDiggWbtc": "0xadc8d7322f2E284c1d9254170dbe311E9D3356cf",
        "native.sushiDiggWbtc": "0xaa8dddfe7DFA3C3269f1910d89E4413dD006D08a",
        "experimental.sushiIBbtcWbtc": "0xf4146A176b09C664978e03d28d07Db4431525dAd",
        "experimental.digg": "0xA6af1B913E205B8E9B95D3B30768c0989e942316",
        "native.hbtcCrv": "0x8c26D9B6B80684CC642ED9eb1Ac1729Af3E819eE",
        "native.pbtcCrv": "0xA9A646668Df5Cec5344941646F5c6b269551e53D",
        "native.obtcCrv": "0x5dd69c6D81f0a403c03b99C5a44Ef2D49b66d388",
        "native.bbtcCrv": "0xF2F3AB09E2D8986fBECbBa59aE838a5418a6680c",
        "native.tricrypto": "0x05ec4356e1acd89cc2d16adc7415c8c95e736ac1",
        "native.tricrypto2": "0x647eeb5C5ED5A71621183f09F6CE8fa66b96827d",
        "native.cvxCrv": "0x826048381d65a65DAa51342C51d464428d301896",
        "native.cvx": "0xBCee2c6CfA7A4e29892c3665f464Be5536F16D95",
        "native.mstableImBtc": "0xd409C506742b7f76f164909025Ab29A47e06d30A",
        "native.mstableFpMbtcHbtc": "0x54D06A0E1cE55a7a60Ee175AbCeaC7e363f603f3",
        "native.vestedCVX": "0x898111d1F4eB55025D0036568212425EE2274082",
        "native.bbveCVX-CVX-f": "0x98Ca7AFa876f0e15494E76E92C5b3658cdE1Ffe1",
        "native.bcrvIbBTC": "0x6D4BA00Fd7BB73b5aa5b3D6180c6f1B0c89f70D1",
        "native.remDigg": "0x4055D395361E73530D43c9D4F18b0668fe4B5b91",
        "native.badgerCrv": "0x1905FD2D2D09792eE058C2b46a05F11630a1EcA1",
    },
    "logic": {
        "StrategyConvexStakingOptimizer": "0x0bB87f40D4eb6066a2311B7BE3B45A3D15771557", # V1.1
        "StrategyCvxHelper": "0x9A12A9141363A5B343B781c4951d42E327B89397", # V1.1
        "StrategyCvxCrvHelper": "0x76328277232c97BAf76D23A69015CB478293A048", # V1.1
        "KeeperAccessControl": "0x4fe70eE8fa906D59A88DE5946F114BdbFC410a80",
        "native.vestedCVX": "0x57961a757bA249E616c1940548401b7CdF83a849", # V1.7
        "RewardsRecoveryStrategy_distribution": "0xEDb5a82016c95B0F6099Ec51F463691Fa2ba02B9",
        "SettV1h": "0x9376B47E7eC9D4cfd5313Dc1FB0DFF4F61E8c481",
        "SettV1_1h_V1": "0x25c9BD2eE36ef38992f8a6BE4CadDA9442Bf4170",
        "SettV4h_V1": "0x0B7Cb84bc7ad4aF3E1C5312987B6E9A4612068AD",
        "SettV1_1h_V2": "0x724f4153b3D69f64975f1B16cE4445fd7bC5C9a2", # V2 -> governanceOrStrategist approve/revoke + sweep 
        "SettV4h_V2": "0x4Da27cD2AE34a9E1776Ed01747A071C17Fa0b2Cf", # V2 -> governanceOrStrategist approve/revoke + sweep 
        "SimpleTimelockWithVoting": "0xb7AcD34643181C879437c2967538D5c0eA42b5D9", # V1.1 -> Beneficiary: devMulti
        "BadgerSettPeak": "0x56bb91BfbeEB5400db72bcE4c15eb0Ddfd06002C", # V1.1
    },
    "guestlists": {
        "bimBTC": "0x7feCCc72aE222e0483cBDE212F5F88De62132546",
        "bFpMbtcHbtc": "0x80348f4430F80b69F8f893B0f0d658e2e7053C1a",
    },
    "controllers": {
        "native": "0x63cF44B2548e4493Fd099222A1eC79F3344D9682",
        "harvest": "0x30392694C25fbBE5C026CF846e9b6525A2aC3eC8",
        "experimental": "0x9b4efA18c0c6b4822225b81D150f3518160f8609",
        "mstable": "0xd35ff2C170CC1e44de4EDdC9f2Fc425C16670250",
        "bbveCVX-CVX-f": "0x0c41A8613fbeFCC8d6e5dF1020DBb336F875247F",
        "ibBTCCrv": "0xe505F7C2FFcce7Ae4b076456BC02A70D8fe8d4d2",
        "restitution": "0x3F61344BA56df00dad9bBcA05d98CA2AeC43Ba0B",
        "badgerCrv_temp": "0xa54d8a596B4022CC4436b692C8ea0E342405eB6e"
    },
    "yearn_vaults": {"byvWBTC": "0x4b92d19c11435614CD49Af1b589001b7c08cD4D5"},
    "peaks": {
        "badgerPeak": "0x41671BA1abcbA387b9b2B752c205e22e916BE6e3",
        "byvWbtcPeak": "0x825218beD8BE0B30be39475755AceE0250C50627",
    },
    "custodians": {"multiswap": "0x533e3c0e6b48010873B947bddC4721b1bDFF9648"},
    "oracles": {
        "oracle": "0x058ec2Bf15011095a25670b618A129c043e2162E",
        "oracle_provider": "0x72dc16CFa95beB42aeebD2B10F22E55bD17Ce976",
    },
    "helpers": {
        "balance_checker": "0xe92261c2D64C363109c36a754A87107142e61b72",
    },
    "rari": {
        "unitroller": "0xe3952d770FB26CC61877CD34Fbc3A3750881e9A1",
        "dai_manager": "0xB465BAF04C087Ce3ed1C266F96CA43f4847D9635",
        "fBADGER-22": "0x6780B4681aa8efE530d075897B3a4ff6cA5ed807",
        "fWBTC-22": "0x352169127E1DA21Ad54788B7c17d990dD1B9C940",
        "fUSDC-22": "0x8e0b2Eb3ebCd55168099806CB865085F461c8Cd8",
        "fDIGG-22": "0x792a676dD661E2c182435aaEfC806F1d4abdC486",
        "fFEI-22": "0x653A32ED7AaA3DB37520125CDB45c17AdB3fdF01",
        "fETH-22": "0xd557C7f29201E296c7b689ef42dc48c9862aFb87",
        "fDAI-22": "0x20D6762fFC948116627d4437C0F0DF7D20198158",
        "fIBBTC-22": "0x6856f0e1BD23c9a1b92f87581Dd2f28E7C84EbcD",
        "fFRAX-22": "0x60fb6aecf861e3f16f7a4dcaddf8d8820244a1cd",
        "fDOLA-22": "0x5117D9453cC9Be8c3fBFbA4aE3B858D18fe45903",
        "fbveCVX-22": "0x26F6F27fDBc3B9cDe4b1943b1c07606CAF2c4C6C",
    },
    "routers": {
        "sushi_router_v2": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
    },
    "fei": {
        "jump_rate_model_fei_eth": "0xbAB47e4B692195BF064923178A90Ef999A15f819",
        "jump_rate_model_fei_dai": "0xEDE47399e2aA8f076d40DC52896331CBa8bd40f7",
    },
    "_deprecated": {
        "native.renCrv": "0x6582a5b139fc1c6360846efdc4440d51aad4df7b",
        "native.sbtcCrv": "0xf1ded284e891943b3e9c657d7fc376b86164ffc2",
        "native.tbtcCrv": "0x522bb024c339a12be1a47229546f288c40b62d29",
        "native.hbtcCrv": "0xff26f400e57bf726822eacbb64fa1c52f1f27988",
        "native.pbtcCrv": "0x1C1fD689103bbFD701b3B7D41A3807F12814033D",
        "native.obtcCrv": "0x2bb864cdb4856ab2d148c5ca52dd7ccec126d138",
        "native.bbtcCrv": "0x4f3e7a4566320b2709fd1986f2e9f84053d3e2a0",
        "native.tricrypto2": "0x2eB6479c2f033360C0F4575A88e3b8909Cbc6a03",
        "native.renCrvV1.1": "0xe66dB6Eb807e6DAE8BD48793E9ad0140a2DEE22A",
        "native.sbtcCrvV1.1": "0x2f278515425c8eE754300e158116930B8EcCBBE1",
        "native.tbtcCrvV1.1": "0x9e0742EE7BECde52A5494310f09aad639AA4790B",
        "native.hbtcCrvV1.1": "0x7354D5119bD42a77E7162c8Afa8A1D18d5Da9cF8",
        "native.pbtcCrvV1.1": "0x3f98F3a21B125414e4740316bd6Ef14718764a22",
        "native.obtcCrvV1.1": "0x50Dd8A61Bdd11Cf5539DAA83Bc8E0F581eD8110a",
        "native.bbtcCrvV1.1": "0xf92660E0fdAfE945aa13616428c9fB4BE19f4d34",
        "native.tricrypto2V1.1": "0xf3202Aa2783F3DEE24a35853C6471db065B05D37",
    },
    "compound": {
        "comptroller": "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B",
    },
    "aave": {
        "incentives_controller": "0xd784927Ff2f95ba542BfC824c8a8a98F3495f6b5",
        "aave_lending_pool_v2": "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
        "data_provider": "0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d",
    },
    "cow": {
        "vault_relayer": "0xC92E8bdf79f0507f65a392b0ab4667716BFE0110",
        "settlement": "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    },
    "ibBTC": {
        "core": "0x2A8facc9D49fBc3ecFf569847833C380A13418a8",
    },
    "convex": {
        "cvxCRV_rewards": "0x3Fe65692bfCD0e6CF84cB1E7d24108E434A7587e",
        "crv_depositor": "0x8014595F2AB54cD7c604B00E9fb932176fDc86Ae",
        "vlCvxExtraRewardDistribution": "0xDecc7d761496d30F30b92Bdf764fb8803c79360D",
        "booster": "0xF403C135812408BFbE8713b5A23a04b3D48AAE31",
        "claim_zap": "0x92Cf9E5e4D1Dfbf7dA0d2BB3e884a68416a65070",
        "vlCVX": "0xD18140b4B819b895A3dba5442F959fA44994AF50",
    },
    "votium": {
        "multiMerkleStash": "0x378Ba9B73309bE80BF4C2c027aAD799766a7ED5A",
    },
    "bribe_tokens_claimable": {
        "CVX": "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
        "BADGER": "0x3472A5A71965499acd81997a54BBA8D852C6E53d",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        "SPELL": "0x090185f2135308bad17527004364ebcc2d37e5f6",
        "ALCX": "0xdbdb4d16eda451d0503b854cf79d55697f90c8df",
        "NSBT": "0x9D79d5B61De59D882ce90125b18F74af650acB93",
        "MATIC": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
        "FXS": "0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0",
        "LDO": "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",
        "TRIBE": "0xc7283b66Eb1EB5FB86327f08e1B5816b0720212B",
        "OGN": "0x8207c1FfC5B6804F6024322CcF34F29c3541Ae26",
        "MTA": "0xa3BeD4E1c75D00fa6f4E5E6922DB7261B5E9AcD2",
        "ANGLE": "0x31429d1856aD1377A8A0079410B297e1a9e214c2",
        "T": "0xCdF7028ceAB81fA0C6971208e83fa7872994beE5",
        "UST": "0xa693B19d2931d498c5B318dF961919BB4aee87a5", # USTv2 (wormhole)
        "LFT": "0xB620Be8a1949AA9532e6a3510132864EF9Bc3F82",
        "FLX": "0x6243d8CEA23066d098a15582d81a598b4e8391F4",
        "GRO": "0x3Ec8798B81485A254928B70CDA1cf0A2BB0B74D7",
    },
    "uniswap": {
        "factoryV3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "v3pool_wbtc_badger": "0xe15e6583425700993bd08F51bF6e7B73cd5da91B",
        "NonfungiblePositionManager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        "routerV2": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "factoryV2": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
    },
    "sushiswap": {
        "routerV2": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
        "factoryV2": "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
    },
    "curve": {
        "provider": "0x0000000022D53366457F9d5E68Ec105046FC4383",
        "factory": "0x0959158b6040D32d04c301A72CBFD6b39E21c9AE",
        "zap_sbtc": "0x7AbDBAf29929e7F8621B757D2a7c04d78d633834",
        "zap_3pool": "0xA79828DF1850E8a3A3064576f380D90aECDD3359",
        "zap_ibbtc": "0xbba4b444FD10302251d9F5797E763b0d912286A1",
        "zap_pbtc": "0x11F419AdAbbFF8d595E7d5b223eee3863Bb3902C",
        "zap_obtc": "0xd5BCf53e2C81e1991570f33Fa881c49EEa570C8D",
    },
    "uma": {
        "DIGG_LongShortPair": "0x65DCcd928C71ef98e6eC887FEA24d116765c8A8D",
    },
    "nft": {
        "badger_jersey": "0xe1e546e25A5eD890DFf8b8D005537c0d373497F8"
    },
    "arbitrum": {
        "outbox": "0x760723CD2e632826c38Fef8CD438A4CC7E7E1A40",
    },
    "balancer": {
        "vault": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
        "gauge_factory": "0x4E7bBd911cf1EFa442BC1b2e9Ea01ffE785412EC",
        "B_50_BTC_50_WETH": "0xA6F548DF93de924d73be7D25dC02554c6bD66dB5",
        "B_20_BTC_80_BADGER_GAUGE": "0xAF50825B010Ae4839Ac444f6c12D44b96819739B",
        "B_20_BTC_80_BADGER": "0xb460DAa847c45f1C4a41cb05BFB3b51c92e41B36",
        "B_3POOL": "0x06Df3b2bbB68adc8B0e302443692037ED9f91b42",
    },
    "hidden_hand": {
        "bribe_vault": "0x9DDb2da7Dd76612e0df237B89AF2CF4413733212",
        "tokenmak_briber": "0x7816b3D0935D668bCfc9A4aaB5a84EBc7fF320cf",
        "balancer_briber": "0x7Cdf753b45AB0729bcFe33DC12401E55d28308A9",
    },
    "chainlink": {
        "feed_registry": "0x47Fb2585D2C56Fe188D0E6ec628a38b74fCeeeDf",
        "keeper_registry": "0x7b3EC232b08BD7b4b3305BE0C044D907B2DF960B",
    },
}

ADDRESSES_IBBTC = {
    "zero": "0x0000000000000000000000000000000000000000",
    "badger_multisig": ADDRESSES_ETH["badger_wallets"]["dev_multisig"],
    "dfdBadgerShared": ADDRESSES_ETH["badger_wallets"]["dfdBadgerShared"],
    "defiDollar_fees": "0x5b5cf8620292249669e1dcc73b753d01543d6ac7",
    "feesink": "0x3b823864cd0cbad8a1f2b65d4807906775becaa7",
    "core": ADDRESSES_ETH["ibBTC"]["core"],
    "ibBTC": ADDRESSES_ETH["treasury_tokens"]["ibBTC"],
    "WBTC": ADDRESSES_ETH["treasury_tokens"]["WBTC"],
    "renBTC": ADDRESSES_ETH["treasury_tokens"]["renBTC"],
    "badgerPeak": ADDRESSES_ETH["peaks"]["badgerPeak"],
    "byvWbtcPeak": ADDRESSES_ETH["peaks"]["byvWbtcPeak"],
    "bcrvRenBTC": ADDRESSES_ETH["sett_vaults"]["bcrvRenBTC"],
    "bcrvSBTC": ADDRESSES_ETH["sett_vaults"]["bcrvSBTC"],
    "bcrvTBTC": ADDRESSES_ETH["sett_vaults"]["bcrvTBTC"],
    "byvWBTC": ADDRESSES_ETH["yearn_vaults"]["byvWBTC"],
    "logic": {
        "core": "0xafa40Da6a373eC4BBfdDAF2e695F3014aF5376c5", # Current logic
        "badgerPeak": "0xbD82A0C250608543b8cAcfD4F0E4438438698df6", # Current logic
        "byvWbtcPeak": "0xA9499b50C4A74000687435A895B55974F079ECaa", # Current logic
    },
    "sett_zap": "0x27Fb47B9Fb32B9cF660C4E0128bE0f4e883f3df1",
    "mint_zap": "0xe8E40093017A3A55B5c2BC3E9CA6a4d208c07734",
    "IbbtcVault_zap": "0x87C3Ef099c6143e4687b060285bad201b9efa493",
    "logic": {
        "IbbtcVault_zap": "0xc5b45ab3d237b0dfc8f8808df39d49ebde8171fe",
    },
}

ADDRESSES_BSC = {
    "zero": "0x0000000000000000000000000000000000000000",
    "badger_wallets": {
        "badgertree": "0x660802Fc641b154aBA66a62137e71f331B6d787A",
        "dev_proxy_admin": "0x6354e79f21b56c11f48bcd7c451be456d7102a36",
        "dev_multisig_deprecated": "0x6DA4c138Dd178F6179091C260de643529A2dAcfe",
        "dev_multisig": "0x329543f0F4BB134A3f7a826DC32532398B38a3fA",
        "ops_multisig": "0x777061674751834993bfBa2269A1F4de5B4a6E7c",
        "ops_deployer": "0xDA25ee226E534d868f0Dd8a459536b03fEE9079b",
        "ops_guardian": "0x29F7F8896Fb913CF7f9949C623F896a154727919",
        "ops_keeper": "0x872213E29C85d7e30F1C8202FC47eD1Ec124BB1D",
    },
    "treasury_tokens": {
        "BADGER": "0x753fbc5800a8C8e3Fb6DC6415810d627A387Dfc9",
        "bBADGER": "0x1F7216fdB338247512Ec99715587bb97BBf96eae",
        "bDIGG": "0x5986D5c77c65e5801a5cAa4fAE80089f870A71dA",
        "BTCb": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
        "WBNB": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
        "CAKE": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
        "cakebBadgerBtcb": "0x10F461CEAC7A17F59e249954Db0784d42EfF5DB5",
        "cakebDiggBtcb": "0xE1E33459505bB3763843a426F7Fd9933418184ae",
        "cakeBnbBtcb": "0x7561EEe90e24F3b348E1087A005F78B4c8453524",
        "cakeBdiggBtcbV2": "0x81d776C90c89B8d51E9497D58338933127e2fA80",
        "cakeBbadgerBtcbV2": "0x5A58609dA96469E9dEf3fE344bC39B00d18eb9A5",
    },
    "lp_tokens": {
        "cakebBadgerBtcb": "0x10F461CEAC7A17F59e249954Db0784d42EfF5DB5",
        "cakebDiggBtcb": "0xE1E33459505bB3763843a426F7Fd9933418184ae",
        "cakeBnbBtcb": "0x7561eee90e24f3b348e1087a005f78b4c8453524",
        "cakeBdiggBtcbV2": "0x81d776C90c89B8d51E9497D58338933127e2fA80",
        "cakeBbadgerBtcbV2": "0x5A58609dA96469E9dEf3fE344bC39B00d18eb9A5",
    },
    "sett_vaults": {
        "bcakeBnbBtcb": "0xaf4B9C4b545D5324904bAa15e29796D2E2f90813",
        "bcakebBadgerBtcb": "0x857F91f735f4B03b19D2b5c6E476C73DB8241F55",
        "bcakebDiggBtcb": "0xa861Ba302674b08f7F2F24381b705870521DDfed",
    },
    "strategies": {
        "cakeBnbBtcb": "0x120BB9F87bAB3C49b89c7745eDC07FED50786534",
        "cakeBdiggBtcbV2": "0xC8C53A293edca5a0146d713b9b95b0cd0a2e5ca4",
        "cakeBbadgerBtcbV2": "0x2A842e01724F10d093aE8a46A01e66DbCf3C7373",
    },
    "coingecko_tokens": {
        "badger-dao": "0x753fbc5800a8C8e3Fb6DC6415810d627A387Dfc9",
        "badger-sett-badger": "0x1F7216fdB338247512Ec99715587bb97BBf96eae",
        "badger-sett-digg": "0x5986D5c77c65e5801a5cAa4fAE80089f870A71dA",
        "binance-bitcoin": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
        "binancecoin": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
        "pancakeswap-token": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
    },
    "airdropable_tokens": {
        "EPS": "0xA7f552078dcC247C2684336020c03648500C6d9F",
    },
    "pancakeswap": {
        "router_v1": "0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F",
        "router_v2": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
        "factory_v2": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    },
}

ADDRESSES_POLYGON = {
    "zero": "0x0000000000000000000000000000000000000000",
    "badger_wallets": {
        "badgertree": "0x2C798FaFd37C7DCdcAc2498e19432898Bc51376b",
        "rewardLogger": "0xd0EE2A5108b8800D688AbC834445fd03b3b2738e",
        "ops_multisig": "0xeb7341c89ba46CC7945f75Bd5dD7a04f8FA16327",
        "dev_multisig": "0x4977110Ed3CD5eC5598e88c8965951a47dd4e738",
    },
    "treasury_tokens": {
        "BADGER": "0x1FcbE5937B0cc2adf69772D228fA4205aCF4D9b2",
    },
    "sett_vaults": {
        "bslpibBTCWbtc": "0xEa8567d84E3e54B32176418B4e0C736b56378961",
        "bqlpUsdcWbtc": "0x6B2d4c4bb50274c5D4986Ff678cC971c0260E967",
        "bcrvRenBTC": "0x7B6bfB88904e4B3A6d239d5Ed8adF557B22C10FC",
        "bcrvTricrypto": "0x85E1cACAe9a63429394d68Db59E14af74143c61c",
    },
    "sett_strategies": {
        "bslpibBTCWbtc": "0xDed61Bd8a8c90596D8A6Cf0e678dA04036146963",
        "bqlpUsdcWbtc": "0x809990849D53a5109e0cb9C446137793B9f6f1Eb",
        "bcrvRenBTC": "0xF8F02D0d41C79a1973f65A440C98acAc7eAA8Dc1",
        "bcrvTricrypto": "0xDb0C3118ef1acA6125200139BEaCc5D675F37c9C",
    },
    "guestLists": {
        "bslpibBTCWbtc": "0x35a1E68d6fe09020C58edf30feE827c9050dB3F5",
        "bqlpUsdcWbtc": "0x6Fba2E04D16Ca67E9E918Ecc9A114d822532159F",
        "bcrvRenBTC": "0xde1E5A892b540334E5434aB7880BDb64c4970579",
    },
    "coingecko_tokens": {
        "WORK": "0x6002410dDA2Fb88b4D0dc3c1D562F7761191eA80",
    },
    "opolis": {
        "stakingHelper": "0x8bF5aD0dBa1e29741740D96E55Bf27Aec30B18E2",
        "whitelist": "0x44a0487656420FDc15f9CA76dd95F3b8a2ef0Baa",
    },
    "registry": "0xFda7eB6f8b7a9e9fCFd348042ae675d1d652454f",
}

ADDRESSES_ARBITRUM = {
    "zero": "0x0000000000000000000000000000000000000000",
    "badger_wallets": {
        "badgertree": "0x635EB2C39C75954bb53Ebc011BDC6AfAAcE115A6",
        "techops_multisig": "0x292549E6bd5a41aE4521Bb8679aDA59631B9eD4C",
        "techops_multisig_deprecated": "0xF6BC36280F32398A031A7294e81131aEE787D178",
        "dev_multisig": "0xb364bAb258ad35dd83c7dd4E8AC78676b7aa1e9F",
        "dev_multisig_deprecated": "0x468A0FF843BC5D185D7B07e4619119259b03619f",
        "ops_deployer2": "0xeE8b29AA52dD5fF2559da2C50b1887ADee257556",
        "ops_deployer4": "0xef42D748e09A2d9eF89238c053CE0B6f00236210",
        "ops_deployer6": "0x96AC69183216074dd8CFA7A380e873380445EaDc",
        "ops_executor1": "0xcf4fF1e03830D692F52EB094c52A5A6A2181Ab3F",
        "ops_executor2": "0x8938bf50d1a3736bdA413510688834540858dAEA",
        "ops_executor3": "0xC69Fb085481bC8C4bfF99B924076656305D9a25D",
        "ops_executor4": "0xBB2281cA5B4d07263112604D1F182AD0Ab26a252",
        "ops_executor8": "0x10C7a2ca16116E5C998Bfa3BC9CEF464475B18ff",
        "ops_executor9": "0x69874C84a30A3742cC2b624238CfEEa24CF5eF82",
        "ops_executor10": "0xaF94D299a73c4545ff702E79D16d9fb1AB5BDAbF",
        "ops_executor11": "0x54cf9df9dcd78e470ab7cb892d7bfbe114c025fc",
        "ops_botsquad": "0xF8dbb94608E72A3C4cEeAB4ad495ac51210a341e",
        "ops_botsquad_cycle0": "0x1a6D6D120a7e3F71B084b4023a518c72F1a93EE9",
    },
    "sett_vaults": {
        "bslpWbtcEth": "0xFc13209cAfE8fb3bb5fbD929eC9F11a39e8Ac041",
        "bslpSushiWeth": "0xe774D1FB3133b037AA17D39165b8F45f444f632d",
        "bcrvRenBTC": "0xBA418CDdd91111F5c1D1Ac2777Fa8CEa28D71843",
        "bcrvTricrypto": "0x4591890225394BF66044347653e112621AF7DDeb",
        "bdxsSwaprWeth": "0x0c2153e8aE4DB8233c61717cDC4c75630E952561",
        "bdxsWbtcWeth": "0xaf9aB64F568149361ab670372b16661f4380e80B",
        "bdxsBadgerWeth": "0xE9C12F06F8AFFD8719263FE4a81671453220389c",
        "bdxsIbbtcWeth": "0x60129b2b762952dfe8b21f40ee8aa3b2a4623546",
    },
    "strategies": {
        "native.renCrv": "0x4C5d19Da5EaeC298B79879a5f7481bEDE055F4F8",
        "native.tricrypto": "0xE83A790fC3B7132fb8d7f8d438Bc5139995BF5f4",
        "native.sushiWbtcEth": "0xA6827f0f14D0B83dB925B616d820434697328c22",
        "native.sushiSushiWEth": "0x86f772C82914f5bFD168f99e208d0FC2C371e9C2",
        "native.DXSSwaprWeth": "0x85386C3cE0679b035a9F8F17f531C076d0b35954",
        "native.DXSWbtcWeth": "0x43942cEae98CC7485B48a37fBB1aa5035e1c8B46",
        "native.DXSBadgerWeth": "0x22F340C2604Dc1cDBe26caC5838Ea9EBC8862a46",
        "native.DXSIbbtcWeth": "0x4AeC063BB5322c9d4c1f46572f432aaE3b78b87c",
    },
    "logic": {
        "native.renCrv": "0x021ea7548Ee9B40d57f47706A605043B05C6c92C", # v1.1
        "native.tricrypto": "0x4Da27cD2AE34a9E1776Ed01747A071C17Fa0b2Cf", # v1.1
        "_deprecated": {
            "native.renCrv": {
                "v1": "0x2eE1E845b601371608b6bA4a4665180dE3b14C85",
            },
            "native.tricrypto": {
                "v1": "0xd64E77C7C6A1dcC7e302F8fe31A22745e223c39c",
            },
        } 
    },
    "treasury_tokens": {
        "BADGER" : "0xbfa641051ba0a0ad1b0acf549a89536a0d76472e",
        "WBTC": "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f",
        "CRV": "0x11cdb42b0eb46d95f990bedd4695a6e3fa034978",
        "SUSHI": "0xd4d42f0b6def4ce0383636770ef773390d85c61a",
        "renBTC": "0xdbf31df14b66535af65aac99c32e9ea844e14501",
        "WETH": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
        "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "SWPR": "0xdE903E2712288A1dA82942DDdF2c20529565aC30",
        "ibBTC": "0x9Ab3FD50FcAe73A1AEDa959468FD0D662c881b42",
        "slpWbtcEth": "0x515e252b2b5c22b4b2b6Df66c2eBeeA871AA4d69",
        "slpSushiWeth": "0x3221022e37029923aCe4235D812273C5A42C322d",
        "slpCrvWeth": "0xbe3B9c3700171183b2B3F827D8833212d0197a96",
        "crvRenBTC": "0x3E01dD8a5E1fb3481F0F589056b428Fc308AF0Fb",
        "crvTricrypto": "0x8e0B8c8BB9db49a46697F3a5Bb8A308e744821D2",
        "dxsSwaprWeth": "0xA66b20912cBEa522278f3056B4aE60D0d3EE271b",
        "dxsWbtcWeth": "0x9A17D97Fb5f76F44604270448Ac77D55Ac40C15c",
        "dxsBadgerWeth": "0x3C6bd88cdD2AECf466E22d4ED86dB6B8953FDb72",
        "dxsIbbtcWeth": "0x6a060a569e04a41794d6b1308865a13F27D27E53",
    },
    "lp_tokens": {
        "slpWbtcEth": "0x515e252b2b5c22b4b2b6Df66c2eBeeA871AA4d69",
        "slpSushiWeth": "0x3221022e37029923aCe4235D812273C5A42C322d",
        "dxsSwaprWeth": "0xA66b20912cBEa522278f3056B4aE60D0d3EE271b",
        "dxsWbtcWeth": "0x9A17D97Fb5f76F44604270448Ac77D55Ac40C15c",
        "dxsBadgerWeth": "0x3C6bd88cdD2AECf466E22d4ED86dB6B8953FDb72",
        "dxsIbbtcWeth": "0x6a060a569e04a41794d6b1308865a13F27D27E53",
    },
    "crv_pools": {
        "crvRenBTC": "0x3E01dD8a5E1fb3481F0F589056b428Fc308AF0Fb",
    },
    "crv_3_pools": {
        "crvTricrypto": "0x960ea3e3C7FB317332d990873d354E18d7645590",
    },
    "coingecko_tokens": {
        "badger-dao": "0xbfa641051ba0a0ad1b0acf549a89536a0d76472e",
        "wrapped-bitcoin": "0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f",
        "curve-dao-token": "0x11cdb42b0eb46d95f990bedd4695a6e3fa034978",
        "sushi": "0xd4d42f0b6def4ce0383636770ef773390d85c61a",
        "renbtc": "0xdbf31df14b66535af65aac99c32e9ea844e14501",
        "weth": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
        "usdx": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "swapr": "0xdE903E2712288A1dA82942DDdF2c20529565aC30",
        "interest-bearing-bitcoin": "0x9Ab3FD50FcAe73A1AEDa959468FD0D662c881b42",
    },
    "guestList": {
        "bDXSSwaprWeth": "0x542629fd10f4F6C71D770C9B3e5478A54e98e3Ea",
        "bDXSWbtcWeth": "0x0c41A8613fbeFCC8d6e5dF1020DBb336F875247F",
    },
    "swapr_staking_contracts": {
        "native.DXSSwaprWeth": "0x0934e27Eea82f720166eC37214C07e6777511D27",
        "native.DXSWbtcWeth": "0x7d5Fb4C81df4115B2e4bB84e36cda8bE7aDF9B4F",
        "native.DXSBadgerWeth": "0x42EcF352216b4Be82331123dbCee60447c91b70F",
        "native.DXSIbbtcWeth": "0x13a22d37Dee5D6C99D4a36F50C2fD274F73Df21c",
    },
    "sushi": {
        "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
    },
    "swapr": {
        "router": "0x530476d5583724A89c8841eB6Da76E7Af4C0F17E"
    },
    "arbitrum_node": "0x00000000000000000000000000000000000000C8",
    "arbitrum_gateway_router": "0x5288c571Fd7aD117beA99bF60FE0846C4E84F933",
    "controller": "0x3811448236d4274705b81C6ab99d617bfab617Cd",
    "rewardsLogger": "0x85E1cACAe9a63429394d68Db59E14af74143c61c",
    "proxyAdminDev": "0x95713d825BcAA799A8e2F2b6c75aeD8b89124852",
    "proxyAdminTimelock": "0xBA77f65a97433d4362Db5c798987d6f0bD28faA3",
    "KeeperAccessControl": "0x265820F3779f652f2a9857133fDEAf115b87db4B",
    "registry": "0xFda7eB6f8b7a9e9fCFd348042ae675d1d652454f",
}

ADDRESSES_BRIDGE = {
    "zero": "0x0000000000000000000000000000000000000000",
    "badger_multisig": ADDRESSES_ETH["badger_wallets"]["dev_multisig"],
    "badger_bridge_team": "0xE95b56685327C9caf83C3e6F0A54b8D9708f32c4",
    "bridge_v1": "0xcB5c2B0FE765069708f17376981C9aFE56Fed339",
    "bridge_v2": "0xb6ea1d3fb9100a2Cf166FEBe11f24367b5FCD24A",
    "WBTC": ADDRESSES_ETH["treasury_tokens"]["WBTC"],
    "renBTC": ADDRESSES_ETH["treasury_tokens"]["renBTC"],
    "renvm_darknodes_fee": "0xE33417797d6b8Aec9171d0d6516E88002fbe23E7",
    "unk_curve_1": "0x2393c368c70b42f055a4932a3fbec2ac9c548011",
    "unk_curve_2": "0xfae8bd34190615f3388f38191dc332b44c53e10b",
}

ADDRESSES_RINKEBY = {
    "badger_wallets": {
        "rinkeby_multisig": "0x6b11a8B734C3eeFd41Ff7b0e2D15F2b0F46D336b",
        "solo_multisig": "0x4e9B82f40a657105b083db308D33E93789329ddb",
    },
    "treasury_tokens": {
        "WBTC": "0x577D296678535e4903D59A4C929B718e1D575e0A",
        "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "LINK": "0x01BE23585060835E02B77ef475b0Cc51aA1e0709",
        "DAI": "0xc7AD46e0b8a400Bb3C915120d284AafbA8fc4735",
        "MKR": "0xF9bA5210F91D0474bd1e1DcDAeC4C58E359AaD85",
        "WETH": "0xc778417E063141139Fce010982780140Aa0cD5Ab",
    },
    "gnosis": {
        "vault_relayer": "0xC92E8bdf79f0507f65a392b0ab4667716BFE0110",
        "settlement": "0x9008D19f58AAbD9eD0D60971565AA8510560ab41",
    },
    "chainlink": {
        "keeper_registry": "0x409CF388DaB66275dA3e44005D182c12EeAa12A0",
    },
}

ADDRESSES_FANTOM = {
    "badger_wallets": {
        "dev_multisig": "0x4c56ee3295042f8A5dfC83e770a21c707CB46f5b",
        "techops_multisig": "0x781E82D5D49042baB750efac91858cB65C6b0582",
        "treasury_ops_multisig": "0xf109c50684EFa12d4dfBF501eD4858F25A4300B3",
        "treasury_vault_multisig": "0x45b798384c236ef0d78311D98AcAEc222f8c6F54",
        "ops_deployer": "0xDA25ee226E534d868f0Dd8a459536b03fEE9079b",
        "ops_deployer2": "0xeE8b29AA52dD5fF2559da2C50b1887ADee257556",
        "ops_deployer6": "0x96AC69183216074dd8CFA7A380e873380445EaDc",
        "ops_executor1": "0xcf4fF1e03830D692F52EB094c52A5A6A2181Ab3F",
        "ops_executor2": "0x8938bf50d1a3736bdA413510688834540858dAEA",
        "ops_executor3": "0xC69Fb085481bC8C4bfF99B924076656305D9a25D",
        "ops_executor4": "0xBB2281cA5B4d07263112604D1F182AD0Ab26a252",
        "ops_executor6": "0x66496eBB9d848C6A8F19612a6Dd10E09954532D0",
        "ops_executor7": "0xaaE2051c2f74920C6662EF5C9B0d602C40D36DF4",
        "ops_executor8": "0x0a9af7FAba0d5DF7A8C881e1B9cd679ee07Af8A2",
        "ops_botsquad": "0xF8dbb94608E72A3C4cEeAB4ad495ac51210a341e",
        "ops_botsquad_cycle0": "0x1a6D6D120a7e3F71B084b4023a518c72F1a93EE9",
    },
    "treasury_tokens": {
        "WFTM": "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83",
        "WETH": "0x74b23882a30290451A17c44f4F05243b6b58C76d",
        "USDC": "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75",
        "OXD": "0xc5A9848b9d145965d821AaeC8fA32aaEE026492d",
    },
    "lp_tokens": {
        "bveOXD-OXD": "0x6519546433dCB0a34A0De908e1032c46906EF664"
    },
    "sett_vaults": {
        "bveOXD": "0x96d4dBdc91Bef716eb407e415c9987a9fAfb8906",
        "bbveOXD-OXD": "0xbF2F3a9ba42A00CA5B18842D8eB1954120e4a2A9"
    },
    "solidly": {
        "router": "0xa38cd27185a464914D3046f0AB9d43356B34829D",
        "factory": "0x3fAaB499b519fdC5819e3D7ed0C26111904cbc28",
    },
    "spookyswap": {
        "router": "0xF491e7B69E4244ad4002BC14e878a34207E38c29",
        "factory": "0x152eE697f2E276fA89E96742e9bB9aB1F2E61bE3"
    }
}


def checksum_address_dict(addresses):
    """
    convert addresses to their checksum variant taken from a (nested) dict
    """
    checksummed = {}
    for k, v in addresses.items():
        if isinstance(v, str):
            checksummed[k] = Web3.toChecksumAddress(v)
        elif isinstance(v, dict):
            checksummed[k] = checksum_address_dict(v)
        else:
            print(k, v, "formatted incorrectly")
    return checksummed


with open('helpers/chaindata.json') as chaindata:
    chain_ids = json.load(chaindata)


registry = DotMap({
    "eth": checksum_address_dict(ADDRESSES_ETH),
    "ibbtc": checksum_address_dict(ADDRESSES_IBBTC),
    "bsc": checksum_address_dict(ADDRESSES_BSC),
    "bridge": checksum_address_dict(ADDRESSES_BRIDGE),
    "poly": checksum_address_dict(ADDRESSES_POLYGON),
    "arbitrum": checksum_address_dict(ADDRESSES_ARBITRUM),
    "rinkeby": checksum_address_dict(ADDRESSES_RINKEBY),
    "ftm": checksum_address_dict(ADDRESSES_FANTOM),
})

# flatten nested dicts and invert the resulting key <-> value
# this allows for reversed lookup of an address
df = pd.json_normalize(registry, sep="_")
reverse = df.T.reset_index().set_index(0)["index"].to_dict()
