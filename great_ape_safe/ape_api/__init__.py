from .aave import Aave
from .anyswap import Anyswap
from .aura import Aura
from .badger import Badger
from .balancer import Balancer
from .bunni import Bunni
from .chainlink import Chainlink
from .compound import Compound
from .convex import Convex
from .cow import Cow
from .curve_v2 import CurveV2
from .curve import Curve
from .euler import Euler
from .maker import Maker
from .opolis import Opolis
from .pancakeswap_v2 import PancakeswapV2
from .rari import Rari
from .snapshot import Snapshot
from .solidly import Solidly
from .spookyswap import Spookyswap
from .sushi import Sushi
from .uni_v2 import UniV2
from .uni_v3 import UniV3


class ApeApis:
    def init_aave(self):
        self.aave = Aave(self)

    def init_anyswap(self):
        self.anyswap = Anyswap(self)

    def init_aura(self):
        self.aura = Aura(self)

    def init_badger(self):
        self.badger = Badger(self)

    def init_balancer(self):
        self.balancer = Balancer(self)

    def init_bunni(self):
        self.bunni = Bunni(self)

    def init_chainlink(self):
        self.chainlink = Chainlink(self)

    def init_compound(self):
        self.compound = Compound(self)

    def init_convex(self):
        self.convex = Convex(self)

    def init_cow(self):
        self.cow = Cow(self)

    def init_curve_v2(self):
        self.curve_v2 = CurveV2(self)

    def init_curve(self):
        self.curve = Curve(self)

    def init_euler(self):
        self.euler = Euler(self)

    def init_maker(self):
        self.maker = Maker(self)

    def init_opolis(self):
        self.opolis = Opolis(self)

    def init_pancakeswap_v2(self):
        self.pancakeswap_v2 = PancakeswapV2(self)

    def init_rari(self):
        self.rari = Rari(self)

    def init_snapshot(self):
        self.snapshot = Snapshot(self)

    def init_solidly(self):
        self.solidly = Solidly(self)

    def init_spookyswap(self):
        self.spookyswap = Spookyswap(self)

    def init_sushi(self):
        self.sushi = Sushi(self)

    def init_uni_v2(self):
        self.uni_v2 = UniV2(self)

    def init_uni_v3(self):
        self.uni_v3 = UniV3(self)
