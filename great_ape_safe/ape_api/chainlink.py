from brownie import interface
from helpers.addresses import r


class Chainlink:
    def __init__(self, safe):
        self.safe = safe

        # contracts
        self.link = self.safe.contract(r.treasury_tokens.LINK, interface.ILinkToken)
        self.keeper_registry = self.safe.contract(
            r.chainlink.keeper_registry, interface.IKeeperRegistry
        )
        self.keeper_registrar = self.safe.contract(
            r.chainlink.keeper_registrar, interface.IKeeperRegistrar
        )

    def register_upkeep(
        self, name, contract_addr, gas_limit, link_mantissa, admin_addr=None
    ):
        """
        ref: https://github.com/smartcontractkit/keeper/blob/master/contracts/UpkeepRegistrationRequests.sol
        """

        admin_addr = self.safe.address if not admin_addr else admin_addr

        data = self.keeper_registrar.register.encode_input(
            name,  # string memory name,
            b"",  # bytes calldata encryptedEmail,
            contract_addr,  # address upkeepContract,
            gas_limit,  # uint32 gasLimit,
            admin_addr,  # address adminAddress,
            b"",  # bytes calldata checkData,
            link_mantissa,  # uint96 amount,
            0,  # uint8 source,
            self.safe.address,  # address sender,
        )

        self.link.transferAndCall(self.keeper_registrar, link_mantissa, data)
