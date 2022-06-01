from brownie import interface
from helpers.addresses import registry


class Chainlink:
    def __init__(self, safe):
        self.safe = safe

        # contracts
        self.relayer = interface.IUpkeepRegistrationRequests(
                registry.eth.chainlink.upkeep_registration_requests,
                owner=safe.account
            )
        self.link = interface.ILinkToken(
            registry.eth.treasury_tokens.LINK, owner=safe.account
        )


    def register_upkeep(
        self, name, contract_addr, gas_limit, link_mantissa, admin_addr=None
    ):
        '''
        ref: https://github.com/smartcontractkit/keeper/blob/master/contracts/UpkeepRegistrationRequests.sol
        '''

        admin_addr = self.safe.address if not admin_addr else admin_addr

        data = self.relayer.register.encode_input(
            name, # string memory name,
            b'', # bytes calldata encryptedEmail,
            contract_addr, # address upkeepContract,
            gas_limit, # uint32 gasLimit,
            admin_addr, # address adminAddress,
            b'', # bytes calldata checkData,
            link_mantissa, # uint96 amount,
            0 # uint8 source
        )

        self.link.transferAndCall(self.relayer, link_mantissa, data)
