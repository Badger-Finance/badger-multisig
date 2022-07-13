from eth_abi import encode_abi

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry

BADGER_BRIDGED = 4285e18
# https://etherscan.io/tx/0x638ed30daa6ab81b96ed9e8a85cce61c95b2159b423d293560966b09f6e5e013
# https://etherscan.io/tx/0x47e96c00c09acd73d90ac603374f209661ac184b9cd41e6d07e749f0141996d7
# values based on the above txs for retrievat/cost L2 retryable ticket
# thinking how to calc this on the flight, so if it works to become a class item
MAX_SUBMISSION_COST = int(0.000003e18)
MAX_GAS = 440_000
GAS_PRICE_BID = 1.5e9


def main():
    # accounts needs eth, leveraging trops in this case
    trops = GreatApeSafe(registry.eth.badger_wallets.treasury_ops_multisig)
    badger = trops.contract(registry.eth.treasury_tokens.BADGER)
    arbitrum_l1_gateway = trops.contract(registry.eth.arbitrum.l1_gateway)

    trops.take_snapshot(tokens=[badger])

    badger.approve(registry.eth.arbitrum.l1_erc20_gateway, BADGER_BRIDGED)

    data = encode_abi(["uint256", "bytes"], [MAX_SUBMISSION_COST, b""])
    # https://github.com/OffchainLabs/arbitrum/blob/89e1f6234fe133253f445db44ec1612d57389c45/docs/sol_contract_docs/md_docs/arb-bridge-peripherals/tokenbridge/ethereum/gateway/L1ArbitrumGateway.md#outboundtransferaddress-_l1token-address-_to-uint256-_amount-uint256-_maxgas-uint256-_gaspricebid-bytes-_data--bytes-res-external
    arbitrum_l1_gateway.outboundTransfer(
        registry.eth.treasury_tokens.BADGER,
        registry.arbitrum.badger_wallets.badgertree,
        BADGER_BRIDGED,
        MAX_GAS,
        GAS_PRICE_BID,
        data,
        {"amount": MAX_SUBMISSION_COST + MAX_GAS * GAS_PRICE_BID},
    )

    trops.post_safe_tx()
