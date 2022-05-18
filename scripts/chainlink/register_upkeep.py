'''
ref: https://github.com/smartcontractkit/keeper/blob/master/contracts/UpkeepRegistrationRequests.sol
'''

from brownie import interface

from great_ape_safe import GreatApeSafe
from helpers.addresses import registry


LINK_MANTISSA = 5e18


def main():
    safe = GreatApeSafe(registry.eth.badger_wallets.techops_multisig)
    relayer = interface.IUpkeepRegistrationRequests(
        registry.eth.chainlink.upkeep_registration_requests, owner=safe.account
    )
    link = interface.ILinkToken(
        registry.eth.treasury_tokens.LINK, owner=safe.account
    )

    data = relayer.register.encode_input(
        'TreeDripper2022Q2', # string memory name,
        b'', # TODO # bytes calldata encryptedEmail,
        registry.eth.drippers.tree_2022_q2, # address upkeepContract,
        400_000, # uint32 gasLimit,
        safe.address, # address adminAddress,
        b'', # bytes calldata checkData,
        LINK_MANTISSA, # uint96 amount,
        0 # TODO # uint8 source
    )

    link.transferAndCall(relayer, LINK_MANTISSA, data)
