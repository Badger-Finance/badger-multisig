from great_ape_safe.ape_api.curve import Curve
from helpers.addresses import registry

class CurveV2(Curve):
    def __init__(self, safe):
        self.safe       = safe
        self.registry   = safe.contract(registry.eth.curve.factory)
        self.max_slippage_and_fees = .02
        self.is_v2 = True
