from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import r

"""
UpKeep references:
gas station: https://automation.chain.link/mainnet/89
treasury voter: https://automation.chain.link/mainnet/42960818007215227498102337773007812241122867237937589685113781988946396009556
tree dripper: https://automation.chain.link/mainnet/16015974269903908984725510916384725148630916297368865448620388766630414318319
rembadger dripper: https://automation.chain.link/mainnet/98030557125143332209375009711552185081207413079136145061022651896587613727137
"""
members = {
    "RemBadgerDripper2023": 98030557125143332209375009711552185081207413079136145061022651896587613727137,
    "TreeDripper2023": 16015974269903908984725510916384725148630916297368865448620388766630414318319,
    "TreasuryVoterModule": 42960818007215227498102337773007812241122867237937589685113781988946396009556,
    # TODO: "GasStationExact": 0 Belongs to old registry, should we cancel it in old registry and register it in the new?
}


def main():
    techops = GreatApeSafe(r.badger_wallets.techops_multisig)
    techops.init_badger()

    # contracts involved
    cl_registry = techops.contract(
        r.chainlink.keeper_registry, interface.IKeeperRegistry
    )
    upkeep_manager = techops.contract(r.badger_wallets.upkeep_manager)

    # 1. Add existing members
    for name, upkeep_id in members.items():
        member_address, gas_limit, _, _, _, _, _, _ = cl_registry.getUpkeep(upkeep_id)
        # https://etherscan.io/address/0x4c02f0160dc0387b13bcb5e1728c780649e109ac#code#F16#L166
        upkeep_manager.addMember(member_address, name, gas_limit, upkeep_id)

    # 2. Include manager in gas st watchlist
    techops.badger.set_gas_station_watchlist()

    techops.post_safe_tx(call_trace=True)
