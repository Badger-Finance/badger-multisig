from .cow import Cow


class ApeApis:
    def init_cow(self, prod=False):
        self.cow = Cow(self, prod=prod)