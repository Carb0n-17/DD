import math
import random
from pathlib import Path

import matplotlib.pyplot as plt

from player import Player
from reel import Reel
from slot_machine import SlotMachine
from symbol import Symbol


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "assets" / "simulations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


REEL_STRIP = [
    "s06",
    "s01",
    "s06",
    "s04",
    "s06",
    "w01",
    "s06",
    "s02",
    "s06",
    "s05",
    "s06",
    "s03",
    "s06",
    "s01",
    "s06",
    "s04",
    "s06",
    "w01",
    "s06",
    "s02",
    "s06",
    "s03",
]

MULTIPLIERS = {
    "w01": 1000.0,
    "s01": 80.0,
    "s02": 40.0,
    "s03": 25.0,
    "s04": 10.0,
    "s05": 10.0,
    "s06": 0.0,
}


def build_slot_machine(wild_weight: float = 1.0, cherry_weight: float = 1.0):
    symbols = [Symbol(name, MULTIPLIERS[name]) for name in REEL_STRIP]

    if wild_weight != 1.0 or cherry_weight != 1.0:
        weighted_symbols = []
        for name in REEL_STRIP:
            weight = wild_weight if name == "w01" else cherry_weight if name == "s05" else 1.0
            weighted_symbols.extend([name] * int(round(weight * 10)))
        symbols = [Symbol(name, MULTIPLIERS[name]) for name in weighted_symbols]

    reels = [Reel(symbols) for _ in range(3)]
    player = Player(100000.0)
    return SlotMachine(reels, player, [0, 0, 0])


def run_monte_carlo(runs: int, bet: float, wild_weight: float = 1.0, cherry_weight: float = 1.0):
    machine = build_slot_machine(wild_weight=wild_weight, cherry_weight=cherry_weight)
    balances = []
    cumulative = 0.0

    for _ in range(runs):
        machine.spin(bet)
        cumulative += machine.win - bet
        balances.append(cumulative)

    return balances


def summarize_results(series):
    return {
        "final_balance": series[-1],
        "mean_per_spin": sum(series) / len(series),
        "stddev": math.sqrt(sum((x - (sum(series) / len(series))) ** 2 for x in series) / len(series)),
        "min": min(series),
        "max": max(series),
    }


def plot_results(results, output_path: Path):
    plt.figure(figsize=(10, 5))
    for label, values in results.items():
        plt.plot(values, label=label, linewidth=1.5)

    plt.title("Monte Carlo Slot Machine Simulation")
    plt.xlabel("Spin")
    plt.ylabel("Cumulative Profit / Loss")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main():
    runs = 5000
    bet = 1.0

    baseline = run_monte_carlo(runs, bet)
    house_edge = run_monte_carlo(runs, bet, wild_weight=0.8, cherry_weight=0.9)

    results = {
        "baseline": baseline,
        "tweaked_house_edge": house_edge,
    }

    plot_results(results, OUTPUT_DIR / "slot_simulation.png")

    for name, values in results.items():
        summary = summarize_results(values)
        print(f"{name}: {summary}")

    print(f"Saved chart to {OUTPUT_DIR / 'slot_simulation.png'}")


if __name__ == "__main__":
    main()
