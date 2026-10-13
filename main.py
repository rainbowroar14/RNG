import ctypes
import json
import math
import random
import shutil
import struct
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk

DOWNLOADS = Path(r"C:\Users\finle\Downloads")
COMBO = DOWNLOADS / "Combo Sound Effect.mp3"
CACHE = Path(tempfile.gettempdir()) / "test-your-luck"
FFMPEG = shutil.which("ffmpeg")
WIDTH = 300
STAGE_H = 160
BAR_H = 38
HEIGHT = STAGE_H + BAR_H
GAME_W = 640
GAME_H = 420
TILE_W = 124
TILE_H = 72
SAVE = Path(__file__).with_name("bestiary.json")
# Rarest first. Each special is its own 1/N check. Anything left is normal.
RARITIES = (
    {"id": "oblivion", "name": "oblivion", "one_in": 1000000000, "odds": "1 in 1000000000", "color": (90, 0, 20)},
    {"id": "eschaton", "name": "eschaton", "one_in": 500000000, "odds": "1 in 500000000", "color": (255, 40, 20)},
    {"id": "apocalypse", "name": "apocalypse", "one_in": 250000000, "odds": "1 in 250000000", "color": (180, 20, 10)},
    {"id": "rapture", "name": "rapture", "one_in": 200000000, "odds": "1 in 200000000", "color": (255, 220, 140)},
    {"id": "limbo", "name": "limbo", "one_in": 100000000, "odds": "1 in 100000000", "color": (80, 80, 90)},
    {"id": "doom", "name": "doom", "one_in": 75000000, "odds": "1 in 75000000", "color": (120, 20, 20)},
    {"id": "entropy", "name": "entropy", "one_in": 50000000, "odds": "1 in 50000000", "color": (140, 120, 160)},
    {"id": "divinity", "name": "divinity", "one_in": 25000000, "odds": "1 in 25000000", "color": (255, 230, 150)},
    {"id": "omniscience", "name": "omniscience", "one_in": 15000000, "odds": "1 in 15000000", "color": (200, 180, 255)},
    {"id": "absolute", "name": "absolute", "one_in": 12000000, "odds": "1 in 12000000", "color": (240, 240, 255)},
    {"id": "primordial", "name": "primordial", "one_in": 11000000, "odds": "1 in 11000000", "color": (140, 80, 90)},
    {"id": "cataclysm", "name": "cataclysm", "one_in": 10500000, "odds": "1 in 10500000", "color": (255, 60, 20)},
    {"id": "paradox", "name": "paradox", "one_in": 10000000, "odds": "1 in 10000000", "color": (4, 2, 12)},
    {"id": "abyss", "name": "abyss", "one_in": 8000000, "odds": "1 in 8000000", "color": (2, 0, 8)},
    {"id": "genesis", "name": "genesis", "one_in": 7000000, "odds": "1 in 7000000", "color": (255, 240, 200)},
    {"id": "continuum", "name": "continuum", "one_in": 6000000, "odds": "1 in 6000000", "color": (80, 90, 160)},
    {"id": "aeon", "name": "aeon", "one_in": 5500000, "odds": "1 in 5500000", "color": (70, 80, 140)},
    {"id": "eternity", "name": "eternity", "one_in": 5000000, "odds": "1 in 5000000", "color": (6, 8, 22)},
    {"id": "firmament", "name": "firmament", "one_in": 4000000, "odds": "1 in 4000000", "color": (40, 70, 150)},
    {"id": "origin", "name": "origin", "one_in": 3000000, "odds": "1 in 3000000", "color": (255, 220, 160)},
    {"id": "nexus", "name": "nexus", "one_in": 2500000, "odds": "1 in 2500000", "color": (160, 80, 220)},
    {"id": "omniverse", "name": "omniverse", "one_in": 2000000, "odds": "1 in 2000000", "color": (120, 60, 220)},
    {"id": "expanse", "name": "expanse", "one_in": 1800000, "odds": "1 in 1800000", "color": (50, 80, 180)},
    {"id": "multiverse", "name": "multiverse", "one_in": 1500000, "odds": "1 in 1500000", "color": (90, 40, 200)},
    {"id": "veil", "name": "veil", "one_in": 1200000, "odds": "1 in 1200000", "color": (100, 70, 140)},
    {"id": "threshold", "name": "threshold", "one_in": 1100000, "odds": "1 in 1100000", "color": (160, 140, 200)},
    {"id": "singularity", "name": "singularity", "one_in": 1000000, "odds": "1 in 1000000", "color": (8, 4, 16)},
    {"id": "aether", "name": "aether", "one_in": 850000, "odds": "1 in 850000", "color": (180, 220, 255)},
    {"id": "cosmos", "name": "cosmos", "one_in": 750000, "odds": "1 in 750000", "color": (30, 60, 160)},
    {"id": "meridian", "name": "meridian", "one_in": 680000, "odds": "1 in 680000", "color": (255, 180, 90)},
    {"id": "horizon", "name": "horizon", "one_in": 600000, "odds": "1 in 600000", "color": (255, 140, 80)},
    {"id": "infinity", "name": "infinity", "one_in": 500000, "odds": "1 in 500000", "color": (220, 220, 255)},
    {"id": "fissure", "name": "fissure", "one_in": 450000, "odds": "1 in 450000", "color": (160, 50, 40)},
    {"id": "rift", "name": "rift", "one_in": 400000, "odds": "1 in 400000", "color": (140, 40, 180)},
    {"id": "portal", "name": "portal", "one_in": 380000, "odds": "1 in 380000", "color": (120, 40, 200)},
    {"id": "wormhole", "name": "wormhole", "one_in": 350000, "odds": "1 in 350000", "color": (80, 40, 140)},
    {"id": "eventide", "name": "eventide", "one_in": 300000, "odds": "1 in 300000", "color": (40, 30, 80)},
    {"id": "twilight", "name": "twilight", "one_in": 270000, "odds": "1 in 270000", "color": (90, 60, 140)},
    {"id": "nebula", "name": "nebula", "one_in": 250000, "odds": "1 in 250000", "color": (180, 60, 200)},
    {"id": "nova", "name": "nova", "one_in": 200000, "odds": "1 in 200000", "color": (255, 160, 60)},
    {"id": "zenith", "name": "zenith", "one_in": 180000, "odds": "1 in 180000", "color": (255, 210, 120)},
    {"id": "apex", "name": "apex", "one_in": 160000, "odds": "1 in 160000", "color": (255, 200, 80)},
    {"id": "constellation", "name": "constellation", "one_in": 150000, "odds": "1 in 150000", "color": (230, 230, 255)},
    {"id": "cluster", "name": "cluster", "one_in": 120000, "odds": "1 in 120000", "color": (160, 120, 230)},
    {"id": "void", "name": "void", "one_in": 100000, "odds": "1 in 100000", "color": (12, 6, 24)},
    {"id": "orbit", "name": "orbit", "one_in": 90000, "odds": "1 in 90000", "color": (80, 160, 220)},
    {"id": "apogee", "name": "apogee", "one_in": 85000, "odds": "1 in 85000", "color": (120, 180, 230)},
    {"id": "satellite", "name": "satellite", "one_in": 80000, "odds": "1 in 80000", "color": (180, 190, 200)},
    {"id": "quasar", "name": "quasar", "one_in": 75000, "odds": "1 in 75000", "color": (255, 236, 160)},
    {"id": "titan", "name": "titan", "one_in": 70000, "odds": "1 in 70000", "color": (190, 170, 130)},
    {"id": "halo", "name": "halo", "one_in": 65000, "odds": "1 in 65000", "color": (230, 230, 180)},
    {"id": "moon", "name": "moon", "one_in": 60000, "odds": "1 in 60000", "color": (210, 210, 200)},
    {"id": "vortex", "name": "vortex", "one_in": 55000, "odds": "1 in 55000", "color": (60, 80, 180)},
    {"id": "universe", "name": "universe", "one_in": 50000, "odds": "1 in 50000", "color": (36, 48, 140)},
    {"id": "ring", "name": "ring", "one_in": 45000, "odds": "1 in 45000", "color": (220, 190, 120)},
    {"id": "band", "name": "band", "one_in": 42000, "odds": "1 in 42000", "color": (210, 180, 90)},
    {"id": "pulsar", "name": "pulsar", "one_in": 40000, "odds": "1 in 40000", "color": (80, 220, 255)},
    {"id": "meteor", "name": "meteor", "one_in": 35000, "odds": "1 in 35000", "color": (255, 120, 40)},
    {"id": "solar", "name": "solar", "one_in": 32000, "odds": "1 in 32000", "color": (255, 200, 60)},
    {"id": "planet", "name": "planet", "one_in": 30000, "odds": "1 in 30000", "color": (70, 140, 210)},
    {"id": "echo", "name": "echo", "one_in": 28000, "odds": "1 in 28000", "color": (140, 180, 220)},
    {"id": "black hole", "name": "black hole", "one_in": 25000, "odds": "1 in 25000", "color": (28, 28, 40)},
    {"id": "flare", "name": "flare", "one_in": 24000, "odds": "1 in 24000", "color": (255, 90, 40)},
    {"id": "prominence", "name": "prominence", "one_in": 23000, "odds": "1 in 23000", "color": (255, 120, 40)},
    {"id": "sun", "name": "sun", "one_in": 22000, "odds": "1 in 22000", "color": (255, 180, 40)},
    {"id": "corona", "name": "corona", "one_in": 21000, "odds": "1 in 21000", "color": (255, 150, 50)},
    {"id": "asteroid", "name": "asteroid", "one_in": 20000, "odds": "1 in 20000", "color": (120, 110, 100)},
    {"id": "aurora", "name": "aurora", "one_in": 18000, "odds": "1 in 18000", "color": (40, 220, 140)},
    {"id": "borealis", "name": "borealis", "one_in": 17500, "odds": "1 in 17500", "color": (40, 200, 160)},
    {"id": "cyclone", "name": "cyclone", "one_in": 17000, "odds": "1 in 17000", "color": (90, 110, 150)},
    {"id": "tempest", "name": "tempest", "one_in": 16500, "odds": "1 in 16500", "color": (70, 90, 130)},
    {"id": "storm", "name": "storm", "one_in": 16000, "odds": "1 in 16000", "color": (70, 80, 110)},
    {"id": "maelstrom", "name": "maelstrom", "one_in": 15500, "odds": "1 in 15500", "color": (40, 60, 110)},
    {"id": "galaxy", "name": "galaxy", "one_in": 15000, "odds": "1 in 15000", "color": (110, 80, 200)},
    {"id": "ion", "name": "ion", "one_in": 14500, "odds": "1 in 14500", "color": (140, 200, 255)},
    {"id": "bolt", "name": "bolt", "one_in": 14000, "odds": "1 in 14000", "color": (255, 230, 80)},
    {"id": "thunder", "name": "thunder", "one_in": 13000, "odds": "1 in 13000", "color": (230, 230, 80)},
    {"id": "spectrum", "name": "spectrum", "one_in": 12500, "odds": "1 in 12500", "color": (200, 80, 180)},
    {"id": "supernova", "name": "supernova", "one_in": 12000, "odds": "1 in 12000", "color": (255, 130, 50)},
    {"id": "collapse", "name": "collapse", "one_in": 11500, "odds": "1 in 11500", "color": (30, 20, 40)},
    {"id": "eclipse", "name": "eclipse", "one_in": 11000, "odds": "1 in 11000", "color": (70, 70, 120)},
    {"id": "chroma", "name": "chroma", "one_in": 10500, "odds": "1 in 10500", "color": (255, 120, 160)},
    {"id": "rainbow", "name": "rainbow", "one_in": 10000, "odds": "1 in 10000", "color": (255, 90, 140)},
    {"id": "prism", "name": "prism", "one_in": 9500, "odds": "1 in 9500", "color": (180, 220, 255)},
    {"id": "nimbus", "name": "nimbus", "one_in": 9200, "odds": "1 in 9200", "color": (200, 210, 230)},
    {"id": "comet", "name": "comet", "one_in": 9000, "odds": "1 in 9000", "color": (170, 215, 255)},
    {"id": "centaur", "name": "centaur", "one_in": 8800, "odds": "1 in 8800", "color": (170, 130, 70)},
    {"id": "pegasus", "name": "pegasus", "one_in": 8500, "odds": "1 in 8500", "color": (230, 230, 240)},
    {"id": "chimera", "name": "chimera", "one_in": 8200, "odds": "1 in 8200", "color": (180, 90, 50)},
    {"id": "griffin", "name": "griffin", "one_in": 8000, "odds": "1 in 8000", "color": (196, 150, 70)},
    {"id": "thunderbird", "name": "thunderbird", "one_in": 7700, "odds": "1 in 7700", "color": (40, 80, 180)},
    {"id": "phoenix", "name": "phoenix", "one_in": 7500, "odds": "1 in 7500", "color": (255, 80, 20)},
    {"id": "roc", "name": "roc", "one_in": 7300, "odds": "1 in 7300", "color": (160, 80, 40)},
    {"id": "wyvern", "name": "wyvern", "one_in": 7200, "odds": "1 in 7200", "color": (80, 140, 70)},
    {"id": "lightning", "name": "lightning", "one_in": 7000, "odds": "1 in 7000", "color": (255, 240, 120)},
    {"id": "manticore", "name": "manticore", "one_in": 6800, "odds": "1 in 6800", "color": (190, 70, 40)},
    {"id": "67", "name": "67", "one_in": 6700, "odds": "1 in 6700", "color": (255, 70, 170)},
    {"id": "cerberus", "name": "cerberus", "one_in": 6600, "odds": "1 in 6600", "color": (50, 40, 40)},
    {"id": "hydra", "name": "hydra", "one_in": 6500, "odds": "1 in 6500", "color": (30, 140, 80)},
    {"id": "basilisk", "name": "basilisk", "one_in": 6300, "odds": "1 in 6300", "color": (50, 140, 60)},
    {"id": "serpent", "name": "serpent", "one_in": 6200, "odds": "1 in 6200", "color": (40, 120, 70)},
    {"id": "kraken", "name": "kraken", "one_in": 6000, "odds": "1 in 6000", "color": (20, 90, 120)},
    {"id": "leviathan", "name": "leviathan", "one_in": 5700, "odds": "1 in 5700", "color": (20, 70, 110)},
    {"id": "talisman", "name": "talisman", "one_in": 5600, "odds": "1 in 5600", "color": (180, 140, 50)},
    {"id": "relic", "name": "relic", "one_in": 5500, "odds": "1 in 5500", "color": (180, 140, 70)},
    {"id": "idol", "name": "idol", "one_in": 5200, "odds": "1 in 5200", "color": (200, 160, 80)},
    {"id": "totem", "name": "totem", "one_in": 5100, "odds": "1 in 5100", "color": (160, 90, 40)},
    {"id": "dragon", "name": "dragon", "one_in": 5000, "odds": "1 in 5000", "color": (170, 28, 36)},
    {"id": "salamander", "name": "salamander", "one_in": 4900, "odds": "1 in 4900", "color": (220, 80, 30)},
    {"id": "sphinx", "name": "sphinx", "one_in": 4800, "odds": "1 in 4800", "color": (196, 160, 90)},
    {"id": "ankh", "name": "ankh", "one_in": 4700, "odds": "1 in 4700", "color": (212, 175, 55)},
    {"id": "scepter", "name": "scepter", "one_in": 4600, "odds": "1 in 4600", "color": (230, 190, 70)},
    {"id": "crown", "name": "crown", "one_in": 4500, "odds": "1 in 4500", "color": (255, 196, 48)},
    {"id": "tiara", "name": "tiara", "one_in": 4300, "odds": "1 in 4300", "color": (230, 210, 140)},
    {"id": "chalice", "name": "chalice", "one_in": 4200, "odds": "1 in 4200", "color": (220, 190, 80)},
    {"id": "alicorn", "name": "alicorn", "one_in": 4100, "odds": "1 in 4100", "color": (255, 180, 220)},
    {"id": "unicorn", "name": "unicorn", "one_in": 4000, "odds": "1 in 4000", "color": (255, 150, 210)},
    {"id": "harp", "name": "harp", "one_in": 3900, "odds": "1 in 3900", "color": (220, 180, 80)},
    {"id": "compass", "name": "compass", "one_in": 3800, "odds": "1 in 3800", "color": (180, 60, 50)},
    {"id": "goblet", "name": "goblet", "one_in": 3600, "odds": "1 in 3600", "color": (210, 180, 90)},
    {"id": "urn", "name": "urn", "one_in": 3550, "odds": "1 in 3550", "color": (190, 150, 70)},
    {"id": "trumpet", "name": "trumpet", "one_in": 3500, "odds": "1 in 3500", "color": (212, 150, 45)},
    {"id": "flute", "name": "flute", "one_in": 3400, "odds": "1 in 3400", "color": (200, 170, 90)},
    {"id": "key", "name": "key", "one_in": 3200, "odds": "1 in 3200", "color": (212, 175, 55)},
    {"id": "locket", "name": "locket", "one_in": 3100, "odds": "1 in 3100", "color": (200, 160, 70)},
    {"id": "treasure", "name": "treasure", "one_in": 3000, "odds": "1 in 3000", "color": (255, 196, 40)},
    {"id": "coin", "name": "coin", "one_in": 2800, "odds": "1 in 2800", "color": (230, 190, 60)},
    {"id": "ingot", "name": "ingot", "one_in": 2700, "odds": "1 in 2700", "color": (190, 160, 50)},
    {"id": "medallion", "name": "medallion", "one_in": 2600, "odds": "1 in 2600", "color": (210, 170, 60)},
    {"id": "emerald", "name": "emerald", "one_in": 2500, "odds": "1 in 2500", "color": (16, 170, 90)},
    {"id": "turquoise", "name": "turquoise", "one_in": 2400, "odds": "1 in 2400", "color": (40, 190, 180)},
    {"id": "jade", "name": "jade", "one_in": 2200, "odds": "1 in 2200", "color": (30, 160, 110)},
    {"id": "beryl", "name": "beryl", "one_in": 2150, "odds": "1 in 2150", "color": (80, 200, 170)},
    {"id": "spinel", "name": "spinel", "one_in": 2100, "odds": "1 in 2100", "color": (220, 60, 90)},
    {"id": "sapphire", "name": "sapphire", "one_in": 2000, "odds": "1 in 2000", "color": (24, 90, 220)},
    {"id": "peridot", "name": "peridot", "one_in": 1900, "odds": "1 in 1900", "color": (140, 210, 60)},
    {"id": "garnet", "name": "garnet", "one_in": 1800, "odds": "1 in 1800", "color": (160, 30, 50)},
    {"id": "citrine", "name": "citrine", "one_in": 1700, "odds": "1 in 1700", "color": (240, 180, 50)},
    {"id": "amethyst", "name": "amethyst", "one_in": 1600, "odds": "1 in 1600", "color": (150, 70, 210)},
    {"id": "tanzanite", "name": "tanzanite", "one_in": 1550, "odds": "1 in 1550", "color": (80, 70, 180)},
    {"id": "amber", "name": "amber", "one_in": 1500, "odds": "1 in 1500", "color": (230, 150, 30)},
    {"id": "pearl", "name": "pearl", "one_in": 1400, "odds": "1 in 1400", "color": (236, 226, 214)},
    {"id": "geode", "name": "geode", "one_in": 1300, "odds": "1 in 1300", "color": (140, 90, 180)},
    {"id": "crystal", "name": "crystal", "one_in": 1200, "odds": "1 in 1200", "color": (180, 235, 255)},
    {"id": "moonstone", "name": "moonstone", "one_in": 1100, "odds": "1 in 1100", "color": (200, 210, 230)},
    {"id": "la peace", "name": "la peace", "one_in": 1000, "odds": "1 in 1000", "color": (18, 42, 150)},
    {"id": "topaz", "name": "topaz", "one_in": 1000, "odds": "1 in 1000", "color": (255, 164, 40)},
    {"id": "onyx", "name": "onyx", "one_in": 900, "odds": "1 in 900", "color": (30, 30, 34)},
    {"id": "opal", "name": "opal", "one_in": 800, "odds": "1 in 800", "color": (190, 170, 255)},
    {"id": "granite", "name": "granite", "one_in": 750, "odds": "1 in 750", "color": (140, 130, 125)},
    {"id": "slate", "name": "slate", "one_in": 720, "odds": "1 in 720", "color": (90, 100, 110)},
    {"id": "titanium", "name": "titanium", "one_in": 700, "odds": "1 in 700", "color": (150, 158, 166)},
    {"id": "flint", "name": "flint", "one_in": 650, "odds": "1 in 650", "color": (80, 80, 85)},
    {"id": "marble", "name": "marble", "one_in": 600, "odds": "1 in 600", "color": (230, 230, 235)},
    {"id": "shale", "name": "shale", "one_in": 580, "odds": "1 in 580", "color": (110, 100, 90)},
    {"id": "basalt", "name": "basalt", "one_in": 550, "odds": "1 in 550", "color": (50, 50, 55)},
    {"id": "ruby", "name": "ruby", "one_in": 500, "odds": "1 in 500", "color": (230, 48, 72)},
    {"id": "coral", "name": "coral", "one_in": 450, "odds": "1 in 450", "color": (255, 110, 120)},
    {"id": "magma", "name": "magma", "one_in": 420, "odds": "1 in 420", "color": (200, 40, 20)},
    {"id": "mythic", "name": "mythic", "one_in": 400, "odds": "1 in 400", "color": (255, 45, 150)},
    {"id": "cinder", "name": "cinder", "one_in": 380, "odds": "1 in 380", "color": (80, 70, 68)},
    {"id": "lava", "name": "lava", "one_in": 350, "odds": "1 in 350", "color": (255, 70, 20)},
    {"id": "ember", "name": "ember", "one_in": 320, "odds": "1 in 320", "color": (255, 90, 30)},
    {"id": "obsidian", "name": "obsidian", "one_in": 300, "odds": "1 in 300", "color": (48, 46, 54)},
    {"id": "frost", "name": "frost", "one_in": 275, "odds": "1 in 275", "color": (190, 220, 255)},
    {"id": "legendary", "name": "legendary", "one_in": 250, "odds": "1 in 250", "color": (255, 196, 64)},
    {"id": "ice", "name": "ice", "one_in": 225, "odds": "1 in 225", "color": (180, 230, 255)},
    {"id": "snow", "name": "snow", "one_in": 210, "odds": "1 in 210", "color": (245, 248, 255)},
    {"id": "platinum", "name": "platinum", "one_in": 200, "odds": "1 in 200", "color": (206, 212, 218)},
    {"id": "hail", "name": "hail", "one_in": 190, "odds": "1 in 190", "color": (200, 220, 230)},
    {"id": "star", "name": "star", "one_in": 175, "odds": "1 in 175", "color": (255, 230, 80)},
    {"id": "diamond", "name": "diamond", "one_in": 150, "odds": "1 in 150", "color": (120, 230, 255)},
    {"id": "gem", "name": "gem", "one_in": 130, "odds": "1 in 130", "color": (80, 220, 200)},
    {"id": "feather", "name": "feather", "one_in": 125, "odds": "1 in 125", "color": (230, 220, 200)},
    {"id": "quartz", "name": "quartz", "one_in": 120, "odds": "1 in 120", "color": (196, 206, 214)},
    {"id": "spark", "name": "spark", "one_in": 110, "odds": "1 in 110", "color": (255, 200, 60)},
    {"id": "bronze", "name": "bronze", "one_in": 100, "odds": "1 in 100", "color": (176, 120, 50)},
    {"id": "clay", "name": "clay", "one_in": 90, "odds": "1 in 90", "color": (176, 110, 80)},
    {"id": "epic", "name": "epic", "one_in": 75, "odds": "1 in 75", "color": (186, 78, 255)},
    {"id": "pebble", "name": "pebble", "one_in": 70, "odds": "1 in 70", "color": (160, 155, 148)},
    {"id": "silver", "name": "silver", "one_in": 60, "odds": "1 in 60", "color": (186, 190, 198)},
    {"id": "brass", "name": "brass", "one_in": 55, "odds": "1 in 55", "color": (190, 160, 70)},
    {"id": "gold", "name": "gold", "one_in": 50, "odds": "1 in 50", "color": (230, 180, 40)},
    {"id": "pyrite", "name": "pyrite", "one_in": 45, "odds": "1 in 45", "color": (180, 160, 50)},
    {"id": "tin", "name": "tin", "one_in": 42, "odds": "1 in 42", "color": (170, 175, 180)},
    {"id": "ash", "name": "ash", "one_in": 40, "odds": "1 in 40", "color": (110, 108, 106)},
    {"id": "cloth", "name": "cloth", "one_in": 38, "odds": "1 in 38", "color": (180, 170, 190)},
    {"id": "string", "name": "string", "one_in": 36, "odds": "1 in 36", "color": (220, 210, 180)},
    {"id": "dust", "name": "dust", "one_in": 35, "odds": "1 in 35", "color": (170, 155, 130)},
    {"id": "chalk", "name": "chalk", "one_in": 33, "odds": "1 in 33", "color": (235, 235, 230)},
    {"id": "soot", "name": "soot", "one_in": 32, "odds": "1 in 32", "color": (90, 88, 86)},
    {"id": "brick", "name": "brick", "one_in": 31, "odds": "1 in 31", "color": (170, 70, 50)},
    {"id": "gravel", "name": "gravel", "one_in": 30, "odds": "1 in 30", "color": (140, 136, 128)},
    {"id": "pinecone", "name": "pinecone", "one_in": 29, "odds": "1 in 29", "color": (130, 90, 50)},
    {"id": "shard", "name": "shard", "one_in": 28, "odds": "1 in 28", "color": (190, 200, 210)},
    {"id": "acorn", "name": "acorn", "one_in": 27, "odds": "1 in 27", "color": (120, 80, 40)},
    {"id": "weed", "name": "weed", "one_in": 26, "odds": "1 in 26", "color": (90, 140, 50)},
    {"id": "rare", "name": "rare", "one_in": 25, "odds": "1 in 25", "color": (72, 156, 255)},
    {"id": "seed", "name": "seed", "one_in": 24, "odds": "1 in 24", "color": (160, 130, 70)},
    {"id": "bark", "name": "bark", "one_in": 23, "odds": "1 in 23", "color": (110, 75, 45)},
    {"id": "twig", "name": "twig", "one_in": 22, "odds": "1 in 22", "color": (140, 100, 60)},
    {"id": "coal", "name": "coal", "one_in": 21, "odds": "1 in 21", "color": (45, 45, 48)},
    {"id": "copper", "name": "copper", "one_in": 20, "odds": "1 in 20", "color": (184, 112, 48)},
    {"id": "rust", "name": "rust", "one_in": 19, "odds": "1 in 19", "color": (166, 82, 42)},
    {"id": "bone", "name": "bone", "one_in": 18, "odds": "1 in 18", "color": (226, 214, 186)},
    {"id": "moss", "name": "moss", "one_in": 17, "odds": "1 in 17", "color": (70, 120, 55)},
    {"id": "dog", "name": "dog", "one_in": 16, "odds": "1 in 16", "color": (150, 100, 55)},
    {"id": "leaf", "name": "leaf", "one_in": 15, "odds": "1 in 15", "color": (58, 156, 48)},
    {"id": "sand", "name": "sand", "one_in": 14, "odds": "1 in 14", "color": (206, 184, 130)},
    {"id": "shell", "name": "shell", "one_in": 13, "odds": "1 in 13", "color": (224, 176, 156)},
    {"id": "cat", "name": "cat", "one_in": 12, "odds": "1 in 12", "color": (230, 140, 70)},
    {"id": "glass", "name": "glass", "one_in": 11, "odds": "1 in 11", "color": (176, 206, 214)},
    {"id": "iron", "name": "iron", "one_in": 10, "odds": "1 in 10", "color": (192, 198, 206)},
    {"id": "paper", "name": "paper", "one_in": 9, "odds": "1 in 9", "color": (235, 230, 210)},
    {"id": "trash", "name": "trash", "one_in": 8, "odds": "1 in 8", "color": (120, 125, 100)},
    {"id": "wood", "name": "wood", "one_in": 7, "odds": "1 in 7", "color": (130, 85, 45)},
    {"id": "sticks", "name": "sticks", "one_in": 6, "odds": "1 in 6", "color": (176, 130, 72)},
    {"id": "uncommon", "name": "uncommon", "one_in": 5, "odds": "1 in 5", "color": (45, 210, 95)},
    {"id": "mud", "name": "mud", "one_in": 4, "odds": "1 in 4", "color": (90, 64, 40)},
    {"id": "dirt", "name": "dirt", "one_in": 4, "odds": "1 in 4", "color": (130, 96, 58)},
    {"id": "stone", "name": "stone", "one_in": 3, "odds": "1 in 3", "color": (150, 146, 140)},
    {"id": "normal", "name": "normal", "one_in": 2, "odds": "1 in 2", "color": (226, 226, 226)},
)
FONT_12 = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 12)
FONT_14 = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 14)
FONT_16 = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 16)
FONT_22 = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 22)
FONT_28 = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 28)
FONT_46 = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 46)
STAR_DIR = Path(__file__).with_name("stars")
PHOTO_DIR = Path(__file__).with_name("photos")
PHOTO_SETS = 5
GREEN = (45, 230, 95, 255)
INK = (244, 244, 244, 255)
# One word per hit in the combo sting. It plays once from the start.
BEATS_MS = (150, 810, 1465, 2115, 2795, 3445, 4130, 4345, 4980, 5195, 5400, 5615)
WORDS = (
    {"text": "Test", "fill": INK, "size": 20, "angle": -14, "x": 68, "y": 34, "drop": 16, "ms": 110, "big": False, "font": "comic.ttf"},
    {"text": "Your", "fill": INK, "size": 20, "angle": 12, "x": 222, "y": 50, "drop": 16, "ms": 110, "big": False, "font": "comic.ttf"},
    {"text": "Luck", "fill": GREEN, "size": 22, "angle": -11, "x": 74, "y": 78, "drop": 14, "ms": 110, "big": False, "font": "comic.ttf"},
    {"text": "Luck", "fill": GREEN, "size": 22, "angle": 10, "x": 214, "y": 96, "drop": 14, "ms": 110, "big": False, "font": "comic.ttf"},
    {"text": "Luck", "fill": GREEN, "size": 24, "angle": -8, "x": 118, "y": 46, "drop": 14, "ms": 110, "big": False, "font": "comic.ttf"},
    {"text": "Luck", "fill": GREEN, "size": 26, "angle": 9, "x": 186, "y": 108, "drop": 14, "ms": 110, "big": False, "font": "comic.ttf"},
    {"text": "Luck", "fill": GREEN, "size": 24, "angle": -12, "x": 58, "y": 100, "drop": 12, "ms": 100, "big": False, "font": "comic.ttf"},
    {"text": "Luck", "fill": GREEN, "size": 28, "angle": 7, "x": 230, "y": 72, "drop": 12, "ms": 100, "big": False, "font": "comic.ttf"},
    {"text": "Luck", "fill": GREEN, "size": 34, "angle": -5, "x": 150, "y": 80, "drop": 16, "ms": 120, "big": True, "font": "comicbd.ttf"},
    {"text": "Luck", "fill": GREEN, "size": 26, "angle": 11, "x": 96, "y": 62, "drop": 10, "ms": 90, "big": False, "font": "comic.ttf"},
    {"text": "Luck", "fill": GREEN, "size": 30, "angle": -9, "x": 206, "y": 88, "drop": 10, "ms": 90, "big": False, "font": "comic.ttf"},
    {"text": "LUCK", "fill": GREEN, "size": 46, "angle": -2, "x": 150, "y": 74, "drop": 64, "ms": 200, "big": True, "font": "comicbd.ttf", "scale": 1.4},
)

winmm = ctypes.windll.winmm
root = tk.Tk()
root.title("Test Your Luck")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(False, False)
root.configure(bg="#141414")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#141414", highlightthickness=0, bd=0)
canvas.pack()

landed: list[dict] = []
falling: list[dict] = []
flash_alpha = 0
play_alpha = 0
intro_done = False
intro_fading = False
music_started = False
playlist: list[Path] = []
track_index = -1
heard_track = False
playing_alias: str | None = None
playing_path: Path | None = None
envelopes: dict[str, dict] = {}
zoom = 1.0
level_smooth = 0.0
prev_level = 0.0
flash_cool = 0
frame_photo: ImageTk.PhotoImage | None = None
play_box = (WIDTH // 2 - 46, STAGE_H - 36, 92, 26)
mode = "intro"
held_start = False
held_name: str | None = None
bestiary_open = False
bestiary_scroll = 0
spinning = False
roll_items: list[dict] = []
roll_times: list[float] = []
roll_started = 0.0
roll_i = -1
show_item: dict | None = None
show_zoom = 1.0
show_alpha = 255
land_zoom = 1.0
land_zoom_target = 1.0
peace_reveal = 1.0
peace_burst = False
particles: list[dict] = []
star_sets: list[list[Image.Image]] = []
photos: dict[str, Image.Image] = {}
pending_result: dict | None = None
last_result: dict | None = None
roll_count = 0
found: dict[str, dict] = {}
money = 0
potion_until = 0.0
speed_until = 0.0
mega_left = 0
roll_pad = 0.06
payout_shown = 0
payout_until = 0.0
shop_open = False
POTION_COST = 750
SPEED_COST = 1500
MEGA_COST = 5000
POTION_SECONDS = 300
ROLL_BOX = (GAME_W // 2 - 74, 196, 148, 34)
DEX_BOX = (GAME_W // 2 - 74, 242, 148, 30)
SHOP_BOX = (GAME_W // 2 - 74, 284, 148, 30)
BUY_LUCK_BOX = (GAME_W // 2 - 220, 200, 140, 32)
BUY_SPEED_BOX = (GAME_W // 2 + 80, 200, 140, 32)
BUY_MEGA_BOX = (GAME_W // 2 - 70, 318, 140, 32)
BACK_BOX = (GAME_W // 2 - 52, GAME_H - 54, 104, 28)


def mci_cmd(command: str) -> int:
    buffer = ctypes.create_unicode_buffer(512)
    return winmm.mciSendStringW(command, buffer, 511, None)


def mci_query(command: str) -> str:
    buffer = ctypes.create_unicode_buffer(512)
    if winmm.mciSendStringW(command, buffer, 511, None):
        return ""
    return buffer.value


def song_list() -> list[Path]:
    found: list[Path] = []
    for number in (1, 2, 3):
        for name in (f"song {number}.mp3", f"Song {number}.mp3", f"song{number}.mp3"):
            path = DOWNLOADS / name
            if path.exists():
                found.append(path)
                break
    used = {path.name.lower() for path in found}
    used.add(COMBO.name.lower())
    if len(found) < 3:
        for path in sorted(DOWNLOADS.glob("*.mp3")):
            if path.name.lower() not in used:
                found.append(path)
                used.add(path.name.lower())
            if len(found) >= 3:
                break
    return found


def stripped(path: Path) -> Path:
    data = path.read_bytes()
    if data[:3] == b"ID3" and len(data) > 10:
        size = ((data[6] & 0x7F) << 21) | ((data[7] & 0x7F) << 14) | ((data[8] & 0x7F) << 7) | (data[9] & 0x7F)
        start = 10 + size
        if data[5] & 0x10:
            start += 10
        if start < len(data) - 1000 and data[start] == 0xFF:
            data = data[start:]
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / ("".join(ch if ch.isalnum() else "_" for ch in path.stem) + ".mp3")
    if not dest.exists() or dest.stat().st_size != len(data):
        dest.write_bytes(data)
    return dest


def load_envelope(path: Path) -> None:
    key = str(path)
    if key in envelopes or not FFMPEG or not path.exists():
        return
    raw = subprocess.run(
        [FFMPEG, "-v", "error", "-i", str(path), "-ac", "1", "-ar", "11025", "-f", "s16le", "-"],
        capture_output=True,
    ).stdout
    count = len(raw) // 2
    if count < 11025:
        return
    samples = struct.unpack("<" + "h" * count, raw[: count * 2])
    hop = 256
    rms: list[float] = []
    for index in range(0, count - hop, hop):
        chunk = samples[index : index + hop]
        rms.append((sum(sample * sample for sample in chunk) / hop) ** 0.5)
    audible = sorted(value for value in rms if value > 40)
    ref = audible[int(len(audible) * 0.9)] if audible else 1.0
    envelopes[key] = {"rms": rms, "hop": hop * 1000 / 11025, "ref": max(ref, 1.0)}


def render_word(spec: dict, scale: float = 1) -> Image.Image:
    size = max(8, int(spec["size"] * scale))
    font = ImageFont.truetype(rf"C:\Windows\Fonts\{spec['font']}", size)
    measure = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    box = measure.textbbox((0, 0), spec["text"], font=font)
    pad = 12
    image = Image.new("RGBA", (box[2] - box[0] + pad * 2, box[3] - box[1] + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(image).text((pad - box[0], pad - box[1]), spec["text"], font=font, fill=spec["fill"])
    return image.rotate(spec["angle"], expand=True, resample=Image.Resampling.BICUBIC)


def blit(base: Image.Image, image: Image.Image, x: float, y: float) -> None:
    base.paste(image, (int(x - image.width / 2), int(y - image.height / 2)), image)


def burst(big: bool) -> None:
    global flash_alpha
    flash_alpha = max(flash_alpha, 210 if big else 88)


def begin_word(index: int) -> None:
    spec = WORDS[index]
    image = render_word(spec, spec.get("scale", 1))
    falling.append(
        {
            "index": index,
            "spec": spec,
            "image": image,
            "start": spec["y"] - spec["drop"],
            "y": spec["y"] - spec["drop"],
            "scale": spec.get("scale", 1),
            "t": 0,
        }
    )
    root.after(16, lambda index=index: step_word(index))


def step_word(index: int) -> None:
    item = next((word for word in falling if word["index"] == index), None)
    if item is None:
        return
    spec = item["spec"]
    item["t"] += 16
    t = min(1.0, item["t"] / spec["ms"])
    eased = 1 - (1 - t) ** 3
    scale = spec.get("scale", 1)
    if scale != 1:
        now = scale + (1 - scale) * eased
        if abs(now - item["scale"]) > 0.08:
            item["scale"] = now
            item["image"] = render_word(spec, now)
    item["y"] = item["start"] + (spec["y"] - item["start"]) * eased
    if t < 1:
        root.after(16, lambda index=index: step_word(index))
        return
    landed.append({"image": render_word(spec, 1), "x": spec["x"], "y": spec["y"]})
    falling.remove(item)
    burst(spec["big"])
    maybe_finish()


def maybe_finish() -> None:
    global intro_fading
    if intro_fading or falling or len(landed) < len(WORDS):
        return
    intro_fading = True
    root.after(280, fade_play)


def start_intro() -> None:
    global playing_alias, playing_path
    if COMBO.exists():
        mci_cmd("play hit")
        playing_alias = "hit"
        playing_path = COMBO
    for index, spec in enumerate(WORDS):
        delay = max(0, BEATS_MS[index] - spec["ms"])
        root.after(delay, lambda index=index: begin_word(index))


def fade_play() -> None:
    global play_alpha, intro_done
    play_alpha = min(255, play_alpha + 14)
    if play_alpha < 255:
        root.after(16, fade_play)
        return
    intro_done = True
    start_playlist()


def sample_level(env: dict, pos: float) -> float:
    idx = int(pos / env["hop"])
    if idx < 0 or idx >= len(env["rms"]):
        return 0.0
    return min(1.0, env["rms"][idx] / env["ref"])


def update_feel() -> tuple[dict | None, float | None]:
    global zoom, level_smooth, prev_level, flash_alpha, flash_cool
    env = envelopes.get(str(playing_path)) if playing_path else None
    pos = None
    level = 0.0
    if playing_alias and mci_query(f"status {playing_alias} mode") == "playing":
        raw = mci_query(f"status {playing_alias} position")
        try:
            pos = float(raw)
        except ValueError:
            pos = None
        if env is not None and pos is not None:
            level = sample_level(env, pos)
    if level > level_smooth:
        level_smooth += (level - level_smooth) * 0.5
    else:
        level_smooth += (level - level_smooth) * 0.14
    zoom = 1 + 0.20 * max(0.0, min(1.0, level_smooth))
    if mode != "game" and level > 0.62 and level - prev_level > 0.16 and flash_cool <= 0:
        flash_alpha = max(flash_alpha, 70)
        flash_cool = 8
    flash_cool = max(0, flash_cool - 1)
    prev_level = level
    return env, pos


def paint_bars(frame: Image.Image, env: dict | None, pos: float | None) -> None:
    pen = ImageDraw.Draw(frame, "RGBA")
    width, height = frame.size
    count = 60
    slot = width / count
    bar_w = max(2, int(slot) - 1)
    bottom = height - 1
    max_h = 86
    for index in range(count):
        level = 0.04
        if env is not None and pos is not None:
            level = sample_level(env, pos - 200 + index * 28)
        height = max(4, int(max_h * (0.05 + 0.95 * level)))
        x = int(index * slot)
        y = bottom - height
        alpha = int(32 + 36 * level)
        pen.rectangle((x, y, x + bar_w, bottom), fill=(206, 142, 36, alpha))
        pen.rectangle((x, y, x + bar_w, min(bottom, y + 2)), fill=(238, 198, 96, alpha + 18))


def paint_button(frame: Image.Image) -> None:
    button = Image.new("RGBA", (play_box[2], play_box[3]), (0, 0, 0, 0))
    pen = ImageDraw.Draw(button)
    pen.rounded_rectangle(
        (1, 1, play_box[2] - 2, play_box[3] - 2),
        radius=6,
        fill=((150, 150, 150, play_alpha) if held_start else (255, 255, 255, play_alpha)),
        outline=(0, 0, 0, play_alpha),
        width=2,
    )
    pen.text((play_box[2] / 2, play_box[3] / 2), "start", font=FONT_12, fill=(0, 0, 0, play_alpha), anchor="mm")
    frame.paste(button, (play_box[0], play_box[1]), button)


def compose(env: dict | None, pos: float | None) -> Image.Image:
    stage = Image.new("RGBA", (WIDTH, STAGE_H), (20, 20, 20, 255))
    for word in landed:
        blit(stage, word["image"], word["x"], word["y"])
    for item in falling:
        blit(stage, item["image"], item["spec"]["x"], item["y"])
    if zoom > 1.004:
        scaled_w = int(WIDTH * zoom)
        scaled_h = int(STAGE_H * zoom)
        scaled = stage.resize((scaled_w, scaled_h), Image.Resampling.BILINEAR)
        left = (scaled_w - WIDTH) // 2
        top = (scaled_h - STAGE_H) // 2
        stage = scaled.crop((left, top, left + WIDTH, top + STAGE_H))
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (20, 20, 20, 255))
    frame.paste(stage, (0, 0))
    paint_bars(frame, env, pos)
    if play_alpha:
        paint_button(frame)
    if flash_alpha:
        veil = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, min(255, int(flash_alpha))))
        frame = Image.alpha_composite(frame, veil)
    return frame


def luck_now() -> int:
    return 2 if time.time() < potion_until else 1


def speed_now() -> int:
    return 2 if time.time() < speed_until else 1


def pick_rarity(boost: int | None = None) -> dict:
    if boost is None:
        boost = luck_now()
    for rarity in RARITIES[:-1]:
        if random.random() < boost / rarity["one_in"]:
            return rarity
    return RARITIES[-1]


def load_progress() -> None:
    global roll_count, found, money, potion_until, speed_until, mega_left
    if not SAVE.exists():
        return
    try:
        data = json.loads(SAVE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    roll_count = int(data.get("rolls", 0))
    money = max(0, int(data.get("money", 0)))
    potion_until = float(data.get("potion_until", 0))
    speed_until = float(data.get("speed_until", 0))
    mega_left = max(0, int(data.get("mega_left", 0)))
    loaded = data.get("found", {})
    if isinstance(loaded, dict):
        found = loaded


def store_progress() -> None:
    SAVE.write_text(
        json.dumps({
            "rolls": roll_count,
            "found": found,
            "money": money,
            "potion_until": potion_until,
            "speed_until": speed_until,
            "mega_left": mega_left,
        }),
        encoding="utf-8",
    )


def money_text(amount: int) -> str:
    return f"${amount:,}"


def potion_clock(seconds: float) -> str:
    whole = max(0, int(math.ceil(seconds)))
    return f"{whole // 60}:{whole % 60:02d}"


def buy_luck() -> None:
    global money, potion_until
    if money < POTION_COST:
        return
    money -= POTION_COST
    potion_until = max(time.time(), potion_until) + POTION_SECONDS
    store_progress()


def buy_speed() -> None:
    global money, speed_until
    if money < SPEED_COST:
        return
    money -= SPEED_COST
    speed_until = max(time.time(), speed_until) + POTION_SECONDS
    store_progress()


def buy_mega() -> None:
    global money, mega_left
    if money < MEGA_COST:
        return
    money -= MEGA_COST
    mega_left += 1
    store_progress()


def yellow_star(path: Path, crop_bottom: float = 1.0) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    if crop_bottom < 1:
        image = image.crop((0, 0, image.width, int(image.height * crop_bottom)))
    box = image.getbbox()
    if box:
        image = image.crop(box)
    image.thumbnail((150, 150), Image.Resampling.LANCZOS)
    blank = Image.new("RGBA", image.size, (255, 210, 42, 0))
    solid = Image.new("RGBA", image.size, (255, 210, 42, 255))
    solid.putalpha(image.getchannel("A"))
    return Image.alpha_composite(blank, solid)


def scribble(image: Image.Image, seed: int) -> Image.Image:
    rng = random.Random(seed)
    width, height = image.size
    shifted = Image.new("RGBA", image.size, (0, 0, 0, 0))
    src = image.load()
    out = shifted.load()
    for y in range(height):
        slide = int(round(math.sin(y * 0.41 + seed) * 2.4 + rng.uniform(-1.4, 1.4)))
        for x in range(width):
            taken = x - slide
            if 0 <= taken < width:
                out[x, y] = src[taken, y]
    warped = Image.new("RGBA", image.size, (0, 0, 0, 0))
    src = shifted.load()
    out = warped.load()
    for x in range(width):
        slide = int(round(math.sin(x * 0.33 + seed * 1.6) * 2.1))
        for y in range(height):
            taken = y - slide
            if 0 <= taken < height:
                out[x, y] = src[x, taken]
    return warped


def photo_set(rarity_id: str) -> str:
    total = sum(ord(char) for char in rarity_id)
    return f"set-{(total % PHOTO_SETS) + 1}"


def load_photos() -> None:
    for rarity in RARITIES:
        path = PHOTO_DIR / photo_set(rarity["id"]) / f"{rarity['id']}.jpg"
        if not path.exists():
            continue
        image = Image.open(path).convert("RGBA")
        side = min(image.size)
        left = (image.width - side) // 2
        top = (image.height - side) // 2
        image = image.crop((left, top, left + side, top + side)).resize((180, 180), Image.Resampling.LANCZOS)
        mask = Image.new("L", image.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 179, 179), radius=18, fill=255)
        image.putalpha(mask)
        photos[rarity["id"]] = image


def load_stars() -> None:
    specs = (
        (STAR_DIR / "hand-drawn-star.png", 0.53),
        (STAR_DIR / "egyptian.png", 1.0),
        (STAR_DIR / "spiral.png", 1.0),
    )
    for path, crop in specs:
        if not path.exists():
            continue
        base = yellow_star(path, crop)
        frames = [base]
        for seed in range(6):
            frames.append(scribble(base, seed + 3))
        star_sets.append(frames)


def duck_music() -> None:
    if playing_alias == "track":
        mci_cmd("setaudio track volume to 300")


def enter_game() -> None:
    global mode
    if mode == "game" or not intro_done:
        return
    mode = "game"
    canvas.config(width=GAME_W, height=GAME_H)
    root.geometry(f"{GAME_W}x{GAME_H}")
    root.update_idletasks()
    if music_started:
        duck_music()
    else:
        start_playlist()


def begin_roll() -> None:
    global spinning, pending_result, roll_items, roll_times, roll_started, roll_i
    global show_zoom, show_alpha, land_zoom, land_zoom_target, peace_reveal, roll_pad, mega_left
    if spinning or bestiary_open or shop_open:
        return
    boost = luck_now()
    if mega_left > 0:
        mega_left -= 1
        boost = 100
        store_progress()
    pending_result = pick_rarity(boost)
    count = 40
    roll_items = [pick_rarity(boost) for _ in range(count - 1)]
    roll_items.append(pending_result)
    roll_times = []
    pace = speed_now()
    moment = 0.14 / pace
    roll_pad = 0.06 / pace
    for index in range(count):
        along = index / (count - 1)
        moment += (0.022 + (0.5 - 0.022) * (along ** 2.8)) / pace
        roll_times.append(moment)
    roll_started = time.perf_counter()
    roll_i = -1
    show_zoom = 1.0
    show_alpha = 255
    land_zoom = 1.0
    land_zoom_target = 1.0
    peace_reveal = 1.0
    particles.clear()
    spinning = True


def spawn_burst(rarity: dict) -> None:
    now = time.perf_counter()
    color = rarity["color"]
    dots = 34 if rarity["id"] == "epic" else 18
    for _ in range(dots):
        angle = random.random() * math.tau
        speed = random.uniform(1.0, 4.2)
        shade = tuple(min(255, max(0, int(channel + random.randint(-24, 40)))) for channel in color)
        particles.append(
            {
                "kind": "dot",
                "x": GAME_W / 2,
                "y": 130,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 1.3,
                "life": random.uniform(0.65, 1.1),
                "color": shade,
                "r": random.randint(2, 5),
            }
        )
    if rarity["id"] == "epic":
        for _ in range(10):
            angle = random.random() * math.tau
            speed = random.uniform(0.8, 3.2)
            particles.append(
                {
                    "kind": "star",
                    "x": GAME_W / 2,
                    "y": 130,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed - 1.1,
                    "life": random.uniform(0.8, 1.25),
                    "color": color if random.random() < 0.7 else (236, 214, 255),
                    "r": random.randint(7, 14),
                    "rot": random.random() * math.tau,
                    "spin": random.uniform(-0.12, 0.12),
                }
            )
    if rarity["id"] == "legendary" and star_sets:
        for _ in range(18):
            angle = random.random() * math.tau
            speed = random.uniform(1.0, 4.8)
            which = random.randrange(len(star_sets))
            particles.append(
                {
                    "kind": "doodle",
                    "x": GAME_W / 2,
                    "y": 130,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed - 1.6,
                    "life": random.uniform(1.0, 1.45),
                    "which": which,
                    "frame": random.randrange(len(star_sets[which])),
                    "scrib": now,
                    "size": random.randint(34, 68),
                    "rot": random.randint(0, 359),
                }
            )


def finish_roll() -> None:
    global spinning, last_result, roll_count, land_zoom_target, peace_reveal, peace_burst
    global money, payout_shown, payout_until
    if pending_result is None:
        spinning = False
        return
    spinning = False
    last_result = pending_result
    roll_count += 1
    money += int(pending_result["one_in"])
    payout_shown = int(pending_result["one_in"])
    payout_until = time.perf_counter() + 1.4
    slot = found.get(pending_result["id"])
    if slot is None:
        found[pending_result["id"]] = {"count": 1, "first": roll_count}
    else:
        slot["count"] = int(slot.get("count", 0)) + 1
    store_progress()
    if pending_result["id"] == "la peace":
        peace_reveal = 0.0
        peace_burst = False
    else:
        spawn_burst(pending_result)
    if pending_result["id"] == "epic":
        land_zoom_target = 1.18
    elif pending_result["id"] == "legendary":
        land_zoom_target = 1.36
    else:
        land_zoom_target = 1.0


def tick_spin() -> None:
    global roll_i, show_item, show_zoom, show_alpha, land_zoom, peace_reveal, peace_burst
    now = time.perf_counter()
    if spinning:
        elapsed = now - roll_started
        while roll_i + 1 < len(roll_items) and elapsed >= roll_times[roll_i + 1]:
            roll_i += 1
            show_item = roll_items[roll_i]
            show_zoom = 1.07
            show_alpha = 60
        if roll_i >= len(roll_items) - 1 and elapsed >= roll_times[-1] + roll_pad:
            finish_roll()
    show_zoom += (1.0 - show_zoom) * 0.42
    show_alpha = min(255, show_alpha + 48)
    land_zoom += (land_zoom_target - land_zoom) * 0.14
    if not spinning and last_result is not None and last_result["id"] == "la peace" and peace_reveal < 1:
        peace_reveal = min(1.0, peace_reveal + 0.018)
        if peace_reveal > 0.45 and not peace_burst:
            peace_burst = True
            spawn_burst(last_result)
    alive: list[dict] = []
    for bit in particles:
        bit["x"] += bit["vx"]
        bit["y"] += bit["vy"]
        bit["vy"] += 0.035
        bit["life"] -= 0.016
        if bit["kind"] == "star":
            bit["rot"] += bit["spin"]
        if bit["kind"] == "doodle" and now - bit["scrib"] >= 0.1:
            frames = star_sets[bit["which"]]
            bit["frame"] = (bit["frame"] + 1) % len(frames)
            bit["scrib"] = now
        if bit["life"] > 0:
            alive.append(bit)
    particles[:] = alive


def point_in(box: tuple[int, int, int, int], x: int, y: int) -> bool:
    bx, by, bw, bh = box
    return bx <= x < bx + bw and by <= y < by + bh


def game_button_at(x: int, y: int) -> str | None:
    if bestiary_open or shop_open:
        if shop_open and point_in(BUY_LUCK_BOX, x, y):
            return "buy"
        if shop_open and point_in(BUY_SPEED_BOX, x, y):
            return "buy-speed"
        if shop_open and point_in(BUY_MEGA_BOX, x, y):
            return "buy-mega"
        return "back" if point_in(BACK_BOX, x, y) else None
    if point_in(ROLL_BOX, x, y):
        return "roll"
    if point_in(DEX_BOX, x, y):
        return "bestiary"
    if point_in(SHOP_BOX, x, y):
        return "shop"
    return None


def paint_ui_button(frame: Image.Image, box: tuple[int, int, int, int], label: str, held: bool, font: ImageFont.FreeTypeFont) -> None:
    x, y, w, h = box
    button = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pen = ImageDraw.Draw(button)
    pen.rounded_rectangle((0, 0, w - 1, h - 1), radius=6, fill=(150, 150, 150, 255) if held else (255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    pen.text((w / 2, h / 2), label, font=font, fill=(0, 0, 0, 255), anchor="mm")
    frame.paste(button, (x, y), button)


def paint_line(frame: Image.Image, text: str, font: ImageFont.FreeTypeFont, color: tuple[int, int, int], cx: float, cy: float, scale: float, alpha: int) -> None:
    if alpha <= 0 or scale <= 0:
        return
    box = font.getbbox(text)
    width = box[2] - box[0] + 8
    height = box[3] - box[1] + 8
    plate = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(plate).text((4 - box[0], 4 - box[1]), text, font=font, fill=(*color, alpha))
    if abs(scale - 1) > 0.012:
        plate = plate.resize((max(1, int(width * scale)), max(1, int(height * scale))), Image.Resampling.BILINEAR)
    frame.paste(plate, (int(cx - plate.width / 2), int(cy - plate.height / 2)), plate)


def star_polygon(cx: float, cy: float, radius: float, rot: float) -> list[tuple[float, float]]:
    points = []
    for index in range(10):
        angle = rot + index * math.pi / 5 - math.pi / 2
        arm = radius if index % 2 == 0 else radius * 0.42
        points.append((cx + math.cos(angle) * arm, cy + math.sin(angle) * arm))
    return points


def paint_particles(frame: Image.Image) -> None:
    pen = ImageDraw.Draw(frame)
    for bit in particles:
        fade = max(0, min(255, int(255 * bit["life"])))
        if bit["kind"] == "dot":
            r = bit["r"]
            pen.ellipse((bit["x"] - r, bit["y"] - r, bit["x"] + r, bit["y"] + r), fill=(*bit["color"], fade))
        elif bit["kind"] == "star":
            pen.polygon(star_polygon(bit["x"], bit["y"], bit["r"], bit["rot"]), fill=(*bit["color"], fade))
        elif bit["kind"] == "doodle":
            frames = star_sets[bit["which"]]
            picture = frames[bit["frame"] % len(frames)]
            size = bit["size"]
            scaled = picture.resize((size, size), Image.Resampling.BILINEAR).rotate(bit["rot"], expand=True, resample=Image.Resampling.BILINEAR)
            if fade < 250:
                scaled.putalpha(scaled.getchannel("A").point(lambda value, fade=fade: value * fade // 255))
            frame.paste(scaled, (int(bit["x"] - scaled.width / 2), int(bit["y"] - scaled.height / 2)), scaled)


def diamond_face() -> dict:
    return next(rarity for rarity in RARITIES if rarity["id"] == "diamond")


def paint_named(frame: Image.Image, rarity: dict, scale: float, alpha: int) -> None:
    name_y = 118
    picture = photos.get(rarity["id"])
    if picture is not None and alpha > 0 and scale > 0:
        size = max(8, int(96 * scale))
        shot = picture.resize((size, size), Image.Resampling.BILINEAR)
        if alpha < 250:
            shot = shot.copy()
            shot.putalpha(shot.getchannel("A").point(lambda value, fade=alpha: value * fade // 255))
        frame.paste(shot, (int(GAME_W / 2 - size / 2), int(58 - size / 2)), shot)
        name_y = 132
    paint_line(frame, rarity["name"], FONT_46, rarity["color"], GAME_W / 2, name_y, scale, alpha)
    paint_line(frame, rarity["odds"], FONT_22, rarity["color"], GAME_W / 2, name_y + 44, scale, alpha)


def paint_roll(frame: Image.Image) -> None:
    elapsed = time.perf_counter() - roll_started if spinning else 0
    scale = show_zoom * (1.0 if spinning else land_zoom)
    if spinning and roll_i < 0 and last_result is not None:
        fade = max(0, int(255 * (1 - elapsed / 0.14)))
        paint_named(frame, last_result, 1, fade)
        return
    shown = show_item if spinning and show_item is not None else last_result
    if shown is None:
        paint_line(frame, "roll", FONT_46, (220, 220, 220), GAME_W / 2, 136, 1, 255)
        return
    alpha = show_alpha if spinning else 255
    if shown["id"] == "la peace" and spinning:
        paint_named(frame, diamond_face(), scale, alpha)
        return
    if shown["id"] == "la peace":
        cover = diamond_face()
        paint_named(frame, cover, scale, int(alpha * (1 - peace_reveal)))
        paint_named(frame, shown, scale, int(alpha * peace_reveal))
        return
    paint_named(frame, shown, scale, alpha)


def paint_bestiary(frame: Image.Image) -> None:
    global bestiary_scroll
    veil = Image.new("RGBA", (GAME_W, GAME_H), (8, 8, 12, 235))
    frame.alpha_composite(veil)
    pen = ImageDraw.Draw(frame)
    pen.text((GAME_W / 2, 36), "bestiary", font=FONT_28, fill=(255, 255, 255, 255), anchor="mm")
    rows = [rarity for rarity in RARITIES if int(found.get(rarity["id"], {}).get("count", 0)) > 0]
    if not rows:
        pen.text((GAME_W / 2, 150), "nothing yet", font=FONT_16, fill=(180, 180, 180, 255), anchor="mm")
    view_top = 68
    view_h = GAME_H - 132
    row_h = 48
    content_h = max(view_h, len(rows) * row_h)
    bestiary_scroll = max(0, min(bestiary_scroll, content_h - view_h))
    sheet = Image.new("RGBA", (GAME_W, content_h), (0, 0, 0, 0))
    sheet_pen = ImageDraw.Draw(sheet)
    for index, rarity in enumerate(rows):
        slot = found[rarity["id"]]
        color = rarity["color"]
        y = index * row_h
        thumb = photos.get(rarity["id"])
        if thumb is not None:
            small = thumb.resize((34, 34), Image.Resampling.BILINEAR)
            sheet.paste(small, (40, y + 7), small)
        sheet_pen.text((88, y + 14), rarity["name"], font=FONT_16, fill=(*color, 255), anchor="lm")
        sheet_pen.text((GAME_W - 88, y + 14), rarity["odds"], font=FONT_14, fill=(210, 210, 210, 255), anchor="rm")
        sheet_pen.text((88, y + 34), f"earliest roll {slot['first']}", font=FONT_12, fill=(200, 200, 200, 255), anchor="lm")
        sheet_pen.text((GAME_W - 88, y + 34), f"got {slot['count']}", font=FONT_12, fill=(200, 200, 200, 255), anchor="rm")
    shown = sheet.crop((0, bestiary_scroll, GAME_W, bestiary_scroll + view_h))
    frame.paste(shown, (0, view_top), shown)
    paint_ui_button(frame, BACK_BOX, "back", held_name == "back", FONT_14)


def paint_shop(frame: Image.Image) -> None:
    veil = Image.new("RGBA", (GAME_W, GAME_H), (16, 16, 18, 255))
    frame.alpha_composite(veil)
    pen = ImageDraw.Draw(frame)
    pen.text((GAME_W / 2, 36), "shop", font=FONT_28, fill=(255, 255, 255, 255), anchor="mm")
    pen.text((GAME_W / 2, 72), money_text(money), font=FONT_22, fill=(45, 230, 95, 255), anchor="mm")
    luck_x = GAME_W // 2 - 150
    speed_x = GAME_W // 2 + 150
    pen.text((luck_x, 118), "2x luck", font=FONT_22, fill=(255, 196, 64, 255), anchor="mm")
    pen.text((speed_x, 118), "2x speed", font=FONT_22, fill=(120, 210, 255, 255), anchor="mm")
    pen.text((luck_x, 150), "5 min", font=FONT_16, fill=(220, 220, 220, 255), anchor="mm")
    pen.text((speed_x, 150), "5 min", font=FONT_16, fill=(220, 220, 220, 255), anchor="mm")
    pen.text((luck_x, 176), "$750", font=FONT_16, fill=(45, 230, 95, 255), anchor="mm")
    pen.text((speed_x, 176), "$1500", font=FONT_16, fill=(120, 210, 255, 255), anchor="mm")
    pen.text((GAME_W / 2, 258), "100x luck", font=FONT_22, fill=(255, 196, 64, 255), anchor="mm")
    pen.text((GAME_W / 2, 286), "next roll", font=FONT_16, fill=(220, 220, 220, 255), anchor="mm")
    pen.text((GAME_W / 2, 308), "$5000", font=FONT_16, fill=(255, 196, 64, 255), anchor="mm")
    paint_ui_button(frame, BUY_LUCK_BOX, "buy", held_name == "buy" or money < POTION_COST, FONT_16)
    paint_ui_button(frame, BUY_SPEED_BOX, "buy", held_name == "buy-speed" or money < SPEED_COST, FONT_16)
    paint_ui_button(frame, BUY_MEGA_BOX, "buy", held_name == "buy-mega" or money < MEGA_COST, FONT_16)
    paint_ui_button(frame, BACK_BOX, "back", held_name == "back", FONT_14)


def paint_luck_timer(frame: Image.Image) -> None:
    now = time.time()
    chips = []
    if speed_until > now:
        chips.append((f"2x  {potion_clock(speed_until - now)}", (120, 210, 255, 255)))
    if potion_until > now:
        chips.append((f"2x  {potion_clock(potion_until - now)}", (45, 230, 95, 255)))
    if mega_left > 0:
        label = "100x next" if mega_left == 1 else f"100x x{mega_left}"
        chips.append((label, (255, 196, 64, 255)))
    pen = ImageDraw.Draw(frame)
    height = 26
    for index, (label, color) in enumerate(chips):
        box = FONT_16.getbbox(label)
        width = box[2] - box[0] + 16
        x = GAME_W - 12 - width
        y = GAME_H - 14 - height - index * (height + 6)
        pen.rounded_rectangle((x, y, x + width, y + height), radius=6, fill=(0, 0, 0, 150))
        pen.text((x + width / 2, y + height / 2), label, font=FONT_16, fill=color, anchor="mm")


def compose_game(env: dict | None, pos: float | None) -> Image.Image:
    frame = Image.new("RGBA", (GAME_W, GAME_H), (16, 16, 18, 255))
    pen = ImageDraw.Draw(frame)
    pen.text((24, 22), f"rolls {roll_count}", font=FONT_14, fill=(220, 220, 220, 255), anchor="lm")
    pen.text((GAME_W - 24, 22), money_text(money), font=FONT_14, fill=(45, 230, 95, 255), anchor="rm")
    if time.perf_counter() < payout_until:
        pen.text((GAME_W - 24, 42), f"+{money_text(payout_shown)}", font=FONT_12, fill=(45, 230, 95, 255), anchor="rm")
    paint_roll(frame)
    paint_bars(frame, env, pos)
    paint_particles(frame)
    if not bestiary_open and not shop_open:
        roll_held = held_name == "roll" or spinning
        paint_ui_button(frame, ROLL_BOX, "rolling" if spinning else "roll", roll_held, FONT_16)
        paint_ui_button(frame, DEX_BOX, "bestiary", held_name == "bestiary", FONT_14)
        paint_ui_button(frame, SHOP_BOX, "shop", held_name == "shop", FONT_14)
    if bestiary_open:
        paint_bestiary(frame)
    if shop_open:
        paint_shop(frame)
    paint_luck_timer(frame)
    return frame


def draw() -> None:
    global frame_photo, flash_alpha
    tick_spin()
    env, pos = update_feel()
    picture = compose_game(env, pos) if mode == "game" else compose(env, pos)
    frame_photo = ImageTk.PhotoImage(picture)
    canvas.delete("all")
    canvas.create_image(0, 0, image=frame_photo, anchor="nw")
    if flash_alpha:
        flash_alpha = max(0, flash_alpha - 18)
    root.after(16, draw)


def start_playlist() -> None:
    global track_index, heard_track, music_started, playing_alias, playing_path
    if music_started or not intro_done:
        return
    music_started = True
    mci_cmd("stop hit")
    mci_cmd("close hit")
    playing_alias = None
    playing_path = None
    playlist[:] = song_list()
    track_index = -1
    heard_track = False
    next_track()


def next_track() -> None:
    global track_index, heard_track, playing_alias, playing_path
    track_index += 1
    mci_cmd("close track")
    playing_alias = None
    if track_index >= len(playlist):
        playing_path = None
        return
    heard_track = False
    path = playlist[track_index]
    if mci_cmd(f'open "{stripped(path)}" type mpegvideo alias track'):
        root.after(40, next_track)
        return
    mci_cmd("set track time format milliseconds")
    mci_cmd("play track")
    playing_alias = "track"
    playing_path = path
    if mode == "game":
        duck_music()
    root.after(400, watch_track)


def watch_track() -> None:
    global heard_track
    if track_index < 0 or track_index >= len(playlist):
        return
    if mci_query("status track mode") == "playing":
        heard_track = True
        root.after(300, watch_track)
    elif heard_track:
        next_track()
    else:
        root.after(150, watch_track)


def on_press(event: tk.Event) -> None:
    global held_start, held_name
    if mode == "intro":
        x, y, w, h = play_box
        held_start = intro_done and x <= event.x < x + w and y <= event.y < y + h
        return
    held_name = game_button_at(event.x, event.y)


def on_release(event: tk.Event) -> None:
    global held_start, held_name, bestiary_open, bestiary_scroll, shop_open
    if mode == "intro":
        x, y, w, h = play_box
        over = intro_done and x <= event.x < x + w and y <= event.y < y + h
        if held_start and over:
            enter_game()
        held_start = False
        return
    chosen = game_button_at(event.x, event.y)
    if held_name and chosen == held_name:
        if chosen == "roll":
            begin_roll()
        elif chosen == "bestiary":
            bestiary_open = True
            shop_open = False
            bestiary_scroll = 0
        elif chosen == "shop":
            shop_open = True
            bestiary_open = False
        elif chosen == "buy":
            buy_luck()
        elif chosen == "buy-speed":
            buy_speed()
        elif chosen == "buy-mega":
            buy_mega()
        elif chosen == "back":
            bestiary_open = False
            shop_open = False
    held_name = None


def close() -> None:
    mci_cmd("close hit")
    mci_cmd("close track")
    root.destroy()


def preload() -> None:
    paths = [COMBO] if COMBO.exists() else []
    paths.extend(song_list())
    for path in paths:
        try:
            load_envelope(path)
        except Exception:
            pass


if len(WORDS) != len(BEATS_MS):
    raise RuntimeError("every beat needs a word")

if COMBO.exists():
    mci_cmd("close hit")
    mci_cmd(f'open "{COMBO}" type mpegvideo alias hit')
    mci_cmd("set hit time format milliseconds")

load_progress()
load_photos()
load_stars()
threading.Thread(target=preload, daemon=True).start()
def on_wheel(event: tk.Event) -> None:
    global bestiary_scroll
    if mode == "game" and bestiary_open:
        bestiary_scroll = max(0, bestiary_scroll - event.delta // 6)


canvas.bind("<Button-1>", on_press)
canvas.bind("<ButtonRelease-1>", on_release)
canvas.bind("<MouseWheel>", on_wheel)
root.protocol("WM_DELETE_WINDOW", close)
draw()
root.after(200, start_intro)
root.mainloop()
