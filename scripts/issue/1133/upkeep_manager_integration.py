from brownie import interface
from great_ape_safe import GreatApeSafe
from helpers.addresses import r

"""
Upkeep references:
gas station: https://automation.chain.link/mainnet/89
treasury voter: https://automation.chain.link/mainnet/42960818007215227498102337773007812241122867237937589685113781988946396009556
tree dripper: https://automation.chain.link/mainnet/16015974269903908984725510916384725148630916297368865448620388766630414318319
rembadger dripper: https://automation.chain.link/mainnet/98030557125143332209375009711552185081207413079136145061022651896587613727137
"""
members = {
    "RemBadgerDripper2023": 98030557125143332209375009711552185081207413079136145061022651896587613727137,
    "TreeDripper2023": 16015974269903908984725510916384725148630916297368865448620388766630414318319,
    "TreasuryVoterModule": 42960818007215227498102337773007812241122867237937589685113781988946396009556,
    "GasStationExact": 89,
}

techops = GreatApeSafe(r.badger_wallets.techops_multisig)
upkeep_manager_snap = GreatApeSafe(r.badger_wallets.upkeep_manager)

# contract
upkeep_manager = techops.contract(r.badger_wallets.upkeep_manager)


def initial_setup():
    """
    carries the following actions: cancels upkeeps from both registries,
    sends techops link funds to manager, init the base upkeep in the manager,
    updates watchlist, updates registry used in the gas station to latest and
    register the gas station so it sends 1 eth to the manager
    """
    techops.init_badger()
    techops.init_chainlink()

    # snaps
    techops.take_snapshot([techops.chainlink.link])
    upkeep_manager_snap.take_snapshot([techops.chainlink.link])

    initial_rounds_top_up = upkeep_manager.roundsTopUp()

    # 1. Send links funds to allow to init base upkeep job
    link_bal = techops.chainlink.link.balanceOf(techops)
    techops.chainlink.link.transfer(upkeep_manager, link_bal)

    # NOTE: reduce the min rounds so we can initialize it, since techops only has 90 LINK
    upkeep_manager.setRoundsTopUp(2)

    # NOTE: while testing with foundry, setting up on this figure have not seen any revert
    # on top-up actions or withdrawal of funds from the keepers.
    # ref of gas snap: https://github.com/Badger-Finance/badger-avatars/blob/main/.gas-snapshot#L166-L176
    upkeep_manager.initializeBaseUpkeep(1_000_000)

    upkeep_manager_snap.print_snapshot()

    # 2. Cancel upkeep in old and new registry to migrate ownership to the upkeep manager
    for name, upkeep_id in members.items():
        if name == "GasStationExact":
            techops.chainlink.keeper_registry_v1_1.cancelUpkeep(upkeep_id)
        else:
            techops.chainlink.keeper_registry.cancelUpkeep(upkeep_id)

    # 3. Update gas station
    techops.badger.set_gas_station_watchlist()

    # 4. Set `s_keeperRegistryAddress` to latest cl registry
    techops.badger.station.setKeeperRegistryAddress(techops.chainlink.keeper_registry)

    # 5. Add gas st in this tx with the left-over link funds to auto-fund the manager in next block with eth
    upkeep_manager.addMember(techops.badger.station, "GasStationExact", 400_000, 0)
    upkeep_manager.setRoundsTopUp(initial_rounds_top_up)

    upkeep_manager_snap.print_snapshot()
    techops.post_safe_tx(call_trace=True)


def register_members_in_manager():
    techops.init_chainlink()

    for name, upkeep_id in members.items():
        if name == "GasStationExact":
            # NOTE: moving forward makes more sense to have links funds in upkeep manager
            techops.chainlink.keeper_registry_v1_1.withdrawFunds(
                upkeep_id, upkeep_manager
            )
        else:
            member_address, gas_limit = techops.chainlink.keeper_registry.getUpkeep(
                upkeep_id
            )[0:2]
            techops.chainlink.keeper_registry.withdrawFunds(upkeep_id, upkeep_manager)
            # https://etherscan.io/address/0x4c02f0160dc0387b13bcb5e1728c780649e109ac#code#F16#L166
            upkeep_manager.addMember(member_address, name, gas_limit, 0)

    techops.post_safe_tx()


def register_dummy_member():
    """
    registers an old dripper to test the flow of registration in the cl registry
    and later being able to cancel
    """
    upkeep_manager.addMember(r.drippers.tree_2022_q2, "TreeDripper2022Q2", 400_000, 0)

    techops.post_safe_tx()


def cancel_dummy_member():
    """
    cancels the old dripper
    """
    upkeep_manager.cancelMemberUpkeep(r.drippers.tree_2022_q2)

    techops.post_safe_tx()
