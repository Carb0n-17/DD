import random

from symbol import Symbol
from typing import List


class Reel:
    def __init__(self, symbols: List[Symbol]):
        self.symbols = symbols

    def spin(self) -> tuple[Symbol, int]:
        index = random.randrange(len(self.symbols))
        return self.symbols[index], index
