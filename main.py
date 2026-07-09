import pygame
import random

from pathlib import Path

IMAGE_DIR = Path("assets/images")

symbols = {}

reel_strip = [
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

PAYOUTS = {
    "w01": {3: 1000},
    "s01": {3: 80},
    "s02": {3: 40},
    "s03": {3: 25},
    "s04": {3: 10},
    "s05": {3: 10, 2: 5, 1: 2},
}

reel_positions = [2, 5, 0]
target_positions = reel_positions.copy()

reel_spinning = [False, False, False]
spin_speed = [1, 1, 1]

stop_time = [0, 0, 0]

width = 960
height = 540
padding = 6
line_size = 3

# Color
BLACK = (0, 0, 0)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
running = True

# Images
for image in IMAGE_DIR.glob("*.png"):
    symbols[image.stem] = pygame.image.load(image).convert_alpha()

# Static background
background = pygame.Surface(screen.get_size())
background.fill((255, 255, 255))
title = font.render("Double Diamond", True, BLACK)
title_rect = title.get_rect(center=(width // 2, 50 + padding * 2))

# Draw static outlines

# Draw outline
pygame.draw.rect(
    background,
    BLACK,
    (padding, padding, width - padding * 2, height - padding * 2),
    line_size,
)

# Draw header
pygame.draw.rect(
    background,
    BLACK,
    (padding * 2, padding * 2, width - padding * 4, 100),
    line_size,
)

# Draw reel area
pygame.draw.rect(
    background,
    BLACK,
    (padding * 2, padding * 2.5 + 100, width - padding * 4, 310),
    line_size,
)

# Draw reel frames
reel_area = pygame.Rect(padding * 2, padding * 2.5 + 100, width - padding * 4, 310)

reel_width = width // 3 - 80
reel_height = 320 - padding * 4
num_reels = 3

gap = (reel_area.width - num_reels * reel_width) // (num_reels + 1)

reels = []

for i in range(num_reels):
    x = reel_area.left + gap + i * (reel_width + gap)
    y = reel_area.centery - reel_height // 2

    reels.append(pygame.Rect(x, y, reel_width, reel_height))

for reel in reels:
    pygame.draw.rect(background, BLACK, reel, line_size)

# Payline
pygame.draw.line(
    background,
    BLACK,
    (reel_area.left + padding, reel_area.centery),
    (reel_area.right - padding, reel_area.centery),
    line_size,
)

# Draw bottom UI
bottom_ui = pygame.Rect(
    padding * 2,
    height - padding * 2 - 100,
    width - padding * 4,
    100,
)

gap = padding // 2
num_boxes = 5

available_width = bottom_ui.width - gap * (num_boxes - 1)

weights = [10, 10, 10, 17, 13]
total = sum(weights)

widths = [available_width * w // total for w in weights]

widths[-1] = available_width - sum(widths[:-1])

boxes = []

x = bottom_ui.left

for w in widths:
    box = pygame.Rect(x, bottom_ui.top, w, bottom_ui.height)
    boxes.append(box)
    x += w + gap

bet_values = [1, 2, 3, 5, 10, 20, 30, 50, 100, 200, 250]
bet_index = 0

balance = 200
win = 0

label_names = ["LINE", "LINE BET", "TOTAL BET", "WIN", "BALANCE"]

labels = []
label_rects = []

for i, box in enumerate(boxes):
    pygame.draw.rect(background, BLACK, box, line_size)

    label = font.render(label_names[i], True, BLACK)
    labels.append(label)

    label_rects.append(label.get_rect(center=(box.centerx, box.centery + 15)))

# REEL
slot_height = reel_height // 5
slot_width = reel.width - padding * 4

lines = 1


def total_bet():
    return lines * bet_values[bet_index]


def evaluate(reel_positions, reel_strip, bet):
    line = [
        reel_strip[reel_positions[0]],
        reel_strip[reel_positions[1]],
        reel_strip[reel_positions[2]],
    ]

    wilds = line.count("w01")

    # Jackpot
    if wilds == 3:
        return PAYOUTS["w01"][3] * bet

    best = 0

    #
    # CHERRIES
    # Wilds DO NOT substitute for cherries.
    #
    cherries = line.count("s05")

    if cherries:
        payout = PAYOUTS["s05"][cherries]

        if wilds == 1:
            payout *= 2
        elif wilds == 2:
            payout *= 4

        best = max(best, payout)

    #
    # Regular symbols (s01-s04)
    # Wilds substitute to maximize the payout.
    #
    for symbol in ("s01", "s02", "s03", "s04"):

        # Ignore blanks and wilds.
        regular = [s for s in line if s not in ("s06", "w01")]

        # Cherries prevent substitution into other symbols.
        if "s05" in regular:
            continue

        # Any remaining symbol must already match.
        if any(s != symbol for s in regular):
            continue

        count = line.count(symbol) + wilds

        payout = PAYOUTS[symbol].get(count, 0)

        if payout == 0:
            continue

        if wilds == 1:
            payout *= 2
        elif wilds == 2:
            payout *= 4

        best = max(best, payout)

    #
    # Mixed bars
    #
    bars = [s for s in line if s in ("s02", "s03", "s04")]

    if bars:
        if len(bars) + wilds == 3:

            # Not three of a kind.
            if len(set(bars)) > 1:

                payout = 5

                if wilds == 1:
                    payout *= 2
                elif wilds == 2:
                    payout *= 4

                best = max(best, payout)

    return best * bet


spin_finished = False

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if bet_index < len(bet_values) - 1:
                    bet_index += 1

            elif event.key == pygame.K_LEFT:
                if bet_index > 0:
                    bet_index -= 1

            elif event.key == pygame.K_RETURN:
                if not any(reel_spinning):

                    bet = total_bet()

                    if balance >= bet:
                        balance -= bet
                        win = 0

                        target_positions = [
                            random.randrange(len(reel_strip)) for _ in range(3)
                        ]

                        reel_spinning = [True, True, True]
                        spin_finished = False

                        now = pygame.time.get_ticks()

                        stop_time[0] = now + 2000
                        stop_time[1] = now + 2500
                        stop_time[2] = now + 3000

    now = pygame.time.get_ticks()

    # Reel 1
    if reel_spinning[0]:
        reel_positions[0] = (reel_positions[0] + 1) % len(reel_strip)

        if now >= stop_time[0] and reel_positions[0] == target_positions[0]:
            reel_spinning[0] = False

    # Reel 2
    if reel_spinning[1]:
        reel_positions[1] = (reel_positions[1] + 1) % len(reel_strip)

        if now >= stop_time[1] and reel_positions[1] == target_positions[1]:
            reel_spinning[1] = False

    # Reel 3
    if reel_spinning[2]:
        reel_positions[2] = (reel_positions[2] + 1) % len(reel_strip)

        if now >= stop_time[2] and reel_positions[2] == target_positions[2]:
            reel_spinning[2] = False

    if not any(reel_spinning) and not spin_finished:
        win = evaluate(
            reel_positions,
            reel_strip,
            bet_values[bet_index],
        )

        balance += win
        spin_finished = True

    # Draw the cached background
    screen.blit(background, (0, 0))
    screen.blit(title, title_rect)

    for reel, position in zip(reels, reel_positions):
        for offset in range(-2, 3):
            symbol = reel_strip[(position + offset) % len(reel_strip)]

            if symbol != "s06":
                image = symbols[symbol]

                max_width = slot_width * 1.2
                max_height = slot_height * 1.2

                scale = min(
                    max_width / image.get_width(),
                    max_height / image.get_height(),
                )

                new_width = int(image.get_width() * scale)
                new_height = int(image.get_height() * scale)

                scaled = pygame.transform.smoothscale(
                    image,
                    (new_width, new_height),
                )

                image_rect = scaled.get_rect(
                    center=(
                        reel.centerx,
                        reel.centery + offset * slot_height,
                    )
                )

                screen.blit(scaled, image_rect)

    value_strings = [
        "1",
        str(bet_values[bet_index]),
        str(bet_values[bet_index]),
        str(win),
        str(balance),
    ]

    for i, box in enumerate(boxes):
        screen.blit(labels[i], label_rects[i])

        value = font.render(value_strings[i], True, BLACK)

        value_rect = value.get_rect(center=(box.centerx, box.centery - 15))

        screen.blit(value, value_rect)

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
