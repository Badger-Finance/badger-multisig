from eth_abi import encode_abi
from great_ape_safe import GreatApeSafe
from helpers.addresses import registry
from brownie import accounts, interface
from rich.console import Console

C = Console()

NEW_LOGIC = registry.eth.logic["uFragments"] 
DEV_PROXY = registry.eth.badger_wallets.devProxyAdmin
TROPS_MSIG = registry.eth.badger_wallets.treasury_ops_multisig
DIGG_ADDRESS = registry.eth.treasury_tokens["DIGG"]

TEST_ADDRESSES = [
    "0xfed1CAe770ca1cD19D7bcC7Fa61d3325A9d5D164",
    "0x03387d5015f88Aea995e790F18eF7FF9dfa0943C",
    "0x4F9a04Bf67a65A59Ef0beB8dcC83f7f3cC5C5D23",
    "0x482c741b0711624d1f462E56EE5D8f776d5970dC",
    "0xD6d2Fcc947e62B21CedbeD336893A2Ba47cd8dac",
    "0x1Da722CfA8B0dFda57CF8D787689039C7A63F049",
    "0x6d0BBe84eBa47434a0004fc65797B87eF1C913b7",
    "0x186E20ae3530520C9F3E6C46F2f5d1062b784761",
    "0x4dc804eaa4c9cC4839f0D9c8824CCE7A0C7Dc10a",
]


def main(queue="true", simulation="false"):
    safe = GreatApeSafe(registry.eth.badger_wallets.dev_multisig)
    safe.init_badger()

    digg = interface.IUFragments(DIGG_ADDRESS, owner=safe.account)
    balance_checker = interface.IBalanceChecker(
        registry.eth.helpers.balance_checker, 
        owner=safe.account
    )

    if queue == "true":
        safe.badger.queue_timelock(
            target_addr=DEV_PROXY,
            signature="upgrade(address,address)",
            data=encode_abi(
                ["address", "address"],
                [digg.address, NEW_LOGIC],
            ),
            dump_dir="data/badger/timelock/upgrade_digg/",
            delay_in_days=4,
        )
    else:   
        # record current digg information
        prev_total_supply = digg.totalSupply()
        prev_name = digg.name()
        prev_decimals = digg.decimals()
        prev_total_shares = digg.totalShares()
        prev_shares_per_fragment = digg._sharesPerFragment()
        prev_owner = digg.owner()
        prev_monetary_policy = digg.monetaryPolicy()
        prev_symbol = digg.symbol()
        prev_initial_shares_per_fragment = digg._initialSharesPerFragment()
        prev_balances = {}
        for address in TEST_ADDRESSES:
            prev_balances[address] = digg.balanceOf(address)

        # Execute upgrade
        if simulation == "true":
            C.print("Simulating upgrade...")
            timelock = accounts.at(registry.eth.governance_timelock, force=True)
            proxyAdmin = interface.IProxyAdmin(DEV_PROXY, owner=timelock)
            proxyAdmin.upgrade(digg.address, NEW_LOGIC)
        else:
            safe.badger.execute_timelock("data/badger/timelock/upgrade_digg/")

        # check storage + random sampled balances
        assert prev_total_supply == digg.totalSupply()
        assert prev_name == digg.name()
        assert prev_decimals == digg.decimals()
        assert prev_total_shares == digg.totalShares()
        assert prev_shares_per_fragment == digg._sharesPerFragment()
        assert prev_owner == digg.owner()
        assert prev_monetary_policy == digg.monetaryPolicy()
        assert prev_symbol == digg.symbol()
        assert prev_initial_shares_per_fragment == digg._initialSharesPerFragment()
        for address in TEST_ADDRESSES:
            assert prev_balances[address] == digg.balanceOf(address)
        prev_trops_msig_balance = digg.balanceOf(TROPS_MSIG)

        # Test new features
        if simulation == "true":
            digg.oneTimeMint({"from": safe.account})

            # Balances remain the same
            for address in TEST_ADDRESSES:
                assert prev_balances[address] == digg.balanceOf(address)

            assert digg.totalSupply() == prev_total_supply + 52942035500

            # Trops balance increase
            new_trops_msig_balance = digg.balanceOf(TROPS_MSIG)
            assert prev_trops_msig_balance + 52942035500 == new_trops_msig_balance

            # test sweep
            # Note: this test assumes there's a balance of link in the digg contract
            link = interface.IERC20(registry.eth.treasury_tokens["LINK"])
            prev_balance = link.balanceOf(digg)
            dev_prev_balance = link.balanceOf(safe.account)
            assert prev_balance > 0
            digg.sweep(link.address, {"from": safe.account})
            assert link.balanceOf(digg) == 0
            assert link.balanceOf(safe.account) == dev_prev_balance + prev_balance

            C.print("[green]Simulation Successful![/green]")

        else:
            # Call oneTimeMint atomically with upgrade execution
            digg.oneTimeMint({"from": safe.account})
            new_trops_msig_balance = digg.balanceOf(TROPS_MSIG)
            assert prev_trops_msig_balance + 52942035500 == new_trops_msig_balance
            # Verify on-chain
            balance_checker.verifyBalance(
                digg.address, 
                TROPS_MSIG,
                prev_trops_msig_balance + 52942035500
            )


    safe.post_safe_tx(post=(simulation!="true"))
