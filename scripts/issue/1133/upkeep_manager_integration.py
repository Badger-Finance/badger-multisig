from brownie import chain
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
INITIAL_ROUNDS_TOP_UP = 20

techops.init_badger()
techops.init_chainlink()


def sim():
    initial_setup_and_testing(sim=True)
    cancel_dummy_member(sim=True)
    cancel_upkeeps(sim=True)
    chain.mine(51)
    register_members_in_manager(sim=True)


def initial_setup_and_testing(sim=False):
    """
    carries the following actions: sends techops link funds to manager,
    init the base upkeep in the manager and adds a dummy member for testing
    """
    # snaps
    techops.take_snapshot([techops.chainlink.link])
    upkeep_manager_snap.take_snapshot([techops.chainlink.link])

    # 1. Send links funds to allow to init base upkeep job
    link_bal = techops.chainlink.link.balanceOf(techops)
    techops.chainlink.link.transfer(upkeep_manager, link_bal)

    # NOTE: reduce the min rounds so we can initialize it, since techops only has 90 LINK
    upkeep_manager.setRoundsTopUp(2)

    # NOTE: while testing with foundry, setting up on this figure have not seen any revert
    # on top-up actions or withdrawal of funds from the keepers.
    # ref of gas snap: https://github.com/Badger-Finance/badger-avatars/blob/main/.gas-snapshot#L166-L176
    upkeep_manager.initializeBaseUpkeep(1_000_000)

    upkeep_manager.addMember(r.drippers.tree_2022_q2, "TreeDripper2022Q2", 400_000, 0)

    upkeep_manager_snap.print_snapshot()
    if not sim:
        techops.post_safe_tx(call_trace=True)


def cancel_upkeeps(sim=False):
    """
    carries the following actions: cancels upkeeps from both registries,
    updates watchlist and updates registry used in the gas station to latest
    """
    # 1. Cancel upkeep in old and new registry to migrate ownership to the upkeep manager
    for name, upkeep_id in members.items():
        if name == "GasStationExact":
            techops.chainlink.keeper_registry_v1_1.cancelUpkeep(upkeep_id)
        else:
            techops.chainlink.keeper_registry.cancelUpkeep(upkeep_id)

    # 2. Update gas station
    techops.badger.set_gas_station_watchlist()

    # 3. Set `s_keeperRegistryAddress` to latest cl registry
    techops.badger.station.setKeeperRegistryAddress(techops.chainlink.keeper_registry)

    if not sim:
        techops.post_safe_tx(call_trace=True)


def register_members_in_manager(sim=False):
    """
    registers all members in the upkeep manager reading the
    target address and gas limit from old and latest cl registry
    """
    for name, upkeep_id in members.items():
        if name == "GasStationExact":
            (
                member_address,
                gas_limit,
            ) = techops.chainlink.keeper_registry_v1_1.getUpkeep(upkeep_id)[0:2]
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

    upkeep_manager.setRoundsTopUp(INITIAL_ROUNDS_TOP_UP)

    if not sim:
        techops.post_safe_tx(call_trace=True)
    else:
        techops.post_safe_tx(skip_preview=True)


def cancel_dummy_member(sim=False):
    """
    cancels the old dripper
    """
    upkeep_manager.cancelMemberUpkeep(r.drippers.tree_2022_q2)

    if not sim:
        techops.post_safe_tx()
