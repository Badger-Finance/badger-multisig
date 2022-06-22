from brownie import web3

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

from ens import ENS
from ens.auto import ns
from eth_abi import encode_abi

target_msigs = [
    "treasury_vault",
    "treasury_ops",
    "treasury_voter",
    "payments",
    "ibbtc",
]


def main():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)

    registry = techops.contract(r.ens.registry)
    resolver = techops.contract(r.ens.public_resolver)

    node = ENS.namehash("badgerdao.eth")

    for msig_name in target_msigs:
        # for example U+005F is not allowed in the name
        # we unify, e.g: treasury_vault becomes treasuryvault
        # ref: https://docs.ens.domains/contract-api-reference/name-processing#normalising-names
        is_valid = ENS.is_valid_name(msig_name)

        if is_valid:
            label = web3.solidityKeccak(["string"], [msig_name])
        else:
            msig_name_unified = msig_name.replace("_", "")
            label = web3.solidityKeccak(["string"], [msig_name_unified])

        # https://etherscan.io/address/0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e#code#L115
        abi_encoded = encode_abi(["bytes32", "bytes32"], [node, label])
        subnode = web3.solidityKeccak(["bytes"], [abi_encoded])

        # https://docs.ens.domains/contract-api-reference/ens#set-subdomain-record
        registry.setSubnodeRecord(node, label, techops.address, resolver.address, 0)

        # https://docs.ens.domains/contract-api-reference/publicresolver#set-ethereum-address
        # why 60? -> https://etherscan.io/address/0x4976fb03c32e5b8cfe2b6ccb31c09ba78ebaba41#code#L128
        resolver.setAddr(subnode, 60, r.badger_wallets[f"{msig_name}_multisig"])

        # check on resolver
        assert resolver.addr(subnode) == r.badger_wallets[f"{msig_name}_multisig"]

        # check by full name
        if is_valid:
            assert (
                ns.address(f"{msig_name}.badgerdao.eth")
                == r.badger_wallets[f"{msig_name}_multisig"]
            )
        else:
            assert (
                ns.address(f"{msig_name_unified}.badgerdao.eth")
                == r.badger_wallets[f"{msig_name}_multisig"]
            )

    techops.post_safe_tx()
