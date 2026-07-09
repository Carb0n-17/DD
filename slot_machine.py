from player import Player
from reel import Reel
from typing import List


class SlotMachine:
    WILD_SYMBOL = "w01"
    CHERRY_SYMBOL = "s05"
    BLANK_SYMBOL = "s06"

    def __init__(self, reels: List[Reel], player: Player, positions: List[int]):
        self.reels = reels
        self.positions = positions
        self.player = player
        self.win = 0

    def spin(self, bet_amount: float) -> bool:
        self.win = 0

        if not self.player.withdraw(bet_amount):
            return False

        results = [reel.spin() for reel in self.reels]
        result_symbols = [result[0] for result in results]
        result_names = [symbol.name for symbol in result_symbols]
        self.positions = [result[1] for result in results]

        if len(set(result_names)) == 1:
            payout = bet_amount * result_symbols[0].multiplier
            self.win = payout
            self.player.deposit(payout)
            return True

        wilds = result_names.count(self.WILD_SYMBOL)
        best_multiplier = 0.0

        cherries = result_names.count(self.CHERRY_SYMBOL)
        if cherries > 0:
            payout_multiplier = 0.0
            if cherries == 1:
                payout_multiplier = 2
            elif cherries == 2:
                payout_multiplier = 5

            if wilds == 1:
                payout_multiplier *= 2
            elif wilds == 2:
                payout_multiplier *= 4

            best_multiplier = max(best_multiplier, payout_multiplier)

        regular_symbols = {
            symbol_name
            for symbol_name in result_names
            if symbol_name
            not in (self.BLANK_SYMBOL, self.WILD_SYMBOL, self.CHERRY_SYMBOL)
        }

        for symbol_name in regular_symbols:
            regular = [
                name
                for name in result_names
                if name not in (self.BLANK_SYMBOL, self.WILD_SYMBOL)
            ]

            if self.CHERRY_SYMBOL in regular:
                continue

            if any(name != symbol_name for name in regular):
                continue

            count = regular.count(symbol_name) + wilds
            if count < 3:
                continue

            payout_symbol = next(
                symbol for symbol in result_symbols if symbol.name == symbol_name
            )
            payout_multiplier = payout_symbol.multiplier * (
                2 if wilds == 1 else 4 if wilds == 2 else 1
            )
            best_multiplier = max(best_multiplier, payout_multiplier)

        bars = [name for name in result_names if name in ("s02", "s03", "s04")]
        if bars and len(bars) + wilds == 3 and len(set(bars)) > 1:
            best_multiplier = max(
                best_multiplier, 5 * (2 if wilds == 1 else 4 if wilds == 2 else 1)
            )

        if best_multiplier > 0:
            self.win = bet_amount * best_multiplier
            self.player.deposit(self.win)

        return True
