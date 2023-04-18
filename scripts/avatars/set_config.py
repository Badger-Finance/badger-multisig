from brownie import ZERO_ADDRESS

from great_ape_safe import GreatApeSafe
from helpers.addresses import r

# owner
trops = GreatApeSafe(r.badger_wallets.treasury_ops_multisig)

# avatars
aura_avatar = trops.contract(r.avatars.aura)
convex_avatar = trops.contract(r.avatars.convex)

# constants
MAX_BPS = 10000
TOKENS_A = [
    r.treasury_tokens.CRV,
    r.treasury_tokens.CVX,
    r.treasury_tokens.FXS,
    r.treasury_tokens.WETH,
    r.treasury_tokens.FRAX,
]
TOKENS_B = [r.treasury_tokens.WETH, r.treasury_tokens.FRAX, r.treasury_tokens.DAI]


# emergency: pausing/unpausing
def pause(avatar_name=None):
    target_avatar = aura_avatar if avatar_name == "aura" else convex_avatar

    target_avatar.pause()

    trops.post_safe_tx()


def unpause(avatar_name=None):
    target_avatar = aura_avatar if avatar_name == "aura" else convex_avatar

    target_avatar.unpause()

    trops.post_safe_tx()


# common setters
def set_manager(avatar_name=None, new_manager=None):
    target_avatar = aura_avatar if avatar_name == "aura" else convex_avatar
    assert new_manager != ZERO_ADDRESS

    target_avatar.setManager(new_manager)

    trops.post_safe_tx()


def set_claim_frequency(avatar_name=None, new_frequency=None):
    new_frequency = int(new_frequency)
    target_avatar = aura_avatar if avatar_name == "aura" else convex_avatar
    current_freq = target_avatar.claimFrequency()
    assert new_frequency > 0 and new_frequency != current_freq

    target_avatar.setClaimFrequency(new_frequency)

    trops.post_safe_tx()


# aura setters
def set_twap_period(new_period=None):
    new_period = int(new_period)
    twap_period = aura_avatar.twapPeriod()
    assert new_period > 0 and new_period != twap_period

    aura_avatar.setTwapPeriod(new_period)

    trops.post_safe_tx()


def set_bps_aura_to_usdc(new_bps=None):
    new_bps = int(new_bps)
    assert new_bps > 0 and new_bps <= MAX_BPS
    aura_avatar.setSellBpsAuraToUsdc(new_bps)

    trops.post_safe_tx()


def set_min_out_bps_bal_to_usdc_min(new_bps=None):
    new_bps = int(new_bps)
    assert (
        new_bps <= MAX_BPS and new_bps < aura_avatar.minOutBpsBalToUsdc().dict()["val"]
    )

    aura_avatar.setMinOutBpsBalToUsdcMin(new_bps)

    trops.post_safe_tx()


def set_min_out_bps_bal_to_usdc_val(new_bps=None):
    new_bps = int(new_bps)
    assert (
        new_bps <= MAX_BPS and new_bps > aura_avatar.minOutBpsBalToUsdc().dict()["min"]
    )

    aura_avatar.setMinOutBpsBalToUsdcVal(new_bps)

    trops.post_safe_tx()


def set_min_out_bps_aura_to_usdc_min(new_bps=None):
    new_bps = int(new_bps)
    assert (
        new_bps <= MAX_BPS and new_bps < aura_avatar.minOutBpsAuraToUsdc().dict()["val"]
    )

    aura_avatar.setMinOutBpsAuraToUsdcMin(new_bps)

    trops.post_safe_tx()


def set_min_out_bps_aura_to_usdc_val(new_bps=None):
    new_bps = int(new_bps)
    assert (
        new_bps <= MAX_BPS and new_bps > aura_avatar.minOutBpsAuraToUsdc().dict()["min"]
    )

    aura_avatar.setMinOutBpsAuraToUsdcVal(new_bps)

    trops.post_safe_tx()


# convex setters
def set_min_out_bps_min(token_a=None, token_b=None, min_new_val=None):
    min_new_val = int(min_new_val)
    assert token_a in TOKENS_A and token_b in TOKENS_B
    assert min_new_val > 0 and min_new_val <= MAX_BPS

    convex_avatar.setMinOutBpsMin(token_a, token_b, min_new_val)

    trops.post_safe_tx()


def set_min_out_bps_val(token_a=None, token_b=None, new_val=None):
    new_val = int(new_val)
    assert token_a in TOKENS_A and token_b in TOKENS_B
    assert new_val > 0 and new_val <= MAX_BPS

    convex_avatar.setMinOutBpsVal(token_a, token_b, new_val)

    trops.post_safe_tx()
