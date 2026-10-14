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
import urllib.request
import uuid
from pathlib import Path

import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk

DOWNLOADS = Path(r"C:\Users\finle\Downloads")
AUDIO_DIR = Path(__file__).resolve().with_name("audio")
if not (AUDIO_DIR / "combo.mp3").exists():
    AUDIO_DIR = Path(__file__).resolve().with_name("web") / "audio"
COMBO = AUDIO_DIR / "combo.mp3"
TICK = AUDIO_DIR / "tick.wav"
if not COMBO.exists():
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
    {"id": "9", "name": "9", "one_in": 999999999, "rarity": 999999999, "odds": "999,999,999", "color": (255, 40, 180)},
    {"id": "apocalypse", "name": "apocalypse", "one_in": 250000000, "odds": "1 in 250000000", "color": (180, 20, 10)},
    {"id": "rapture", "name": "rapture", "one_in": 200000000, "odds": "1 in 200000000", "color": (255, 220, 140)},
    {"id": "limbo", "name": "limbo", "one_in": 100000000, "odds": "1 in 100000000", "color": (80, 80, 90)},
    {"id": "doom", "name": "doom", "one_in": 75000000, "odds": "1 in 75000000", "color": (120, 20, 20)},
    {"id": "entropy", "name": "entropy", "one_in": 50000000, "odds": "1 in 50000000", "color": (140, 120, 160)},
    {"id": "divinity", "name": "divinity", "one_in": 25000000, "odds": "1 in 25000000", "color": (255, 230, 150)},
    {"id": "8", "name": "8", "one_in": 88888888, "rarity": 88888888, "odds": "88,888,888", "color": (80, 220, 255)},
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
    {"id": "7", "name": "7", "one_in": 7777777, "rarity": 7777777, "odds": "7,777,777", "color": (180, 80, 255)},
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
    {"id": "6", "name": "6", "one_in": 666666, "rarity": 666666, "odds": "666,666", "color": (255, 70, 90)},
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
    {"id": "5", "name": "5", "one_in": 55555, "rarity": 55555, "odds": "55,555", "color": (255, 140, 40)},
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
    {"id": "67", "name": "67", "one_in": 6700, "rarity": 676767, "odds": "676,767", "color": (255, 70, 170)},
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
    {"id": "4", "name": "4", "one_in": 4444, "rarity": 4444, "odds": "4,444", "color": (255, 210, 60)},
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
    {"id": "3", "name": "3", "one_in": 333, "rarity": 333, "odds": "333", "color": (80, 220, 120)},
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
    {"id": "2", "name": "2", "one_in": 22, "rarity": 22, "odds": "22", "color": (80, 160, 255)},
    {"id": "wood", "name": "wood", "one_in": 7, "odds": "1 in 7", "color": (130, 85, 45)},
    {"id": "sticks", "name": "sticks", "one_in": 6, "odds": "1 in 6", "color": (176, 130, 72)},
    {"id": "uncommon", "name": "uncommon", "one_in": 5, "odds": "1 in 5", "color": (45, 210, 95)},
    {"id": "mud", "name": "mud", "one_in": 4, "odds": "1 in 4", "color": (90, 64, 40)},
    {"id": "dirt", "name": "dirt", "one_in": 4, "odds": "1 in 4", "color": (130, 96, 58)},
    {"id": "stone", "name": "stone", "one_in": 3, "odds": "1 in 3", "color": (150, 146, 140)},
    {"id": "tiny", "name": "tiny", "one_in": 2, "rarity": 2, "odds": "2", "color": (186, 196, 210)},
    {"id": "medium", "name": "medium", "one_in": 3, "rarity": 3, "odds": "3", "color": (90, 150, 210)},
    {"id": "splash", "name": "splash", "one_in": 4, "rarity": 4, "odds": "4", "color": (70, 190, 230)},
    {"id": "fire", "name": "fire", "one_in": 6, "rarity": 6, "odds": "6", "color": (255, 110, 30)},
    {"id": "lucky", "name": "lucky", "one_in": 25, "rarity": 25, "odds": "25", "color": (48, 180, 72)},
    {"id": "super lucky", "name": "super lucky", "one_in": 252, "rarity": 252, "odds": "252", "color": (36, 200, 96)},
    {"id": "ultra lucky", "name": "ultra lucky", "one_in": 777, "rarity": 777, "odds": "777", "color": (255, 206, 48)},
    {"id": "1", "name": "1", "one_in": 1, "rarity": 1, "odds": "1", "color": (210, 220, 235)},
    {"id": "normal", "name": "normal", "one_in": 2, "odds": "1 in 2", "color": (226, 226, 226)},
    {"id": "🐉", "name": "🐉", "one_in": 1600, "rarity": 1600, "odds": "1,600", "color": (233, 193, 143)},
    {"id": "🦄", "name": "🦄", "one_in": 1949, "rarity": 1949, "odds": "1,949", "color": (124, 54, 234)},
    {"id": "🌈", "name": "🌈", "one_in": 2373, "rarity": 2373, "odds": "2,373", "color": (84, 74, 204)},
    {"id": "🔥", "name": "🔥", "one_in": 2890, "rarity": 2890, "odds": "2,890", "color": (121, 141, 151)},
    {"id": "💎", "name": "💎", "one_in": 3519, "rarity": 3519, "odds": "3,519", "color": (114, 104, 124)},
    {"id": "👑", "name": "👑", "one_in": 4286, "rarity": 4286, "odds": "4,286", "color": (197, 157, 157)},
    {"id": "⚡", "name": "⚡", "one_in": 5220, "rarity": 5220, "odds": "5,220", "color": (193, 213, 163)},
    {"id": "🌟", "name": "🌟", "one_in": 6357, "rarity": 6357, "odds": "6,357", "color": (215, 175, 225)},
    {"id": "🌙", "name": "🌙", "one_in": 7742, "rarity": 7742, "odds": "7,742", "color": (173, 133, 153)},
    {"id": "🍀", "name": "🍀", "one_in": 9428, "rarity": 9428, "odds": "9,428", "color": (176, 226, 196)},
    {"id": "💰", "name": "💰", "one_in": 11482, "rarity": 11482, "odds": "11,482", "color": (112, 222, 192)},
    {"id": "🎲", "name": "🎲", "one_in": 13983, "rarity": 13983, "odds": "13,983", "color": (74, 124, 204)},
    {"id": "🏆", "name": "🏆", "one_in": 17029, "rarity": 17029, "odds": "17,029", "color": (94, 204, 104)},
    {"id": "💀", "name": "💀", "one_in": 20738, "rarity": 20738, "odds": "20,738", "color": (136, 66, 126)},
    {"id": "👻", "name": "👻", "one_in": 25255, "rarity": 25255, "odds": "25,255", "color": (131, 91, 151)},
    {"id": "🎃", "name": "🎃", "one_in": 30757, "rarity": 30757, "odds": "30,757", "color": (135, 215, 235)},
    {"id": "🌸", "name": "🌸", "one_in": 37457, "rarity": 37457, "odds": "37,457", "color": (60, 50, 100)},
    {"id": "🌺", "name": "🌺", "one_in": 45616, "rarity": 45616, "odds": "45,616", "color": (134, 184, 124)},
    {"id": "🍄", "name": "🍄", "one_in": 55553, "rarity": 55553, "odds": "55,553", "color": (144, 134, 74)},
    {"id": "🦋", "name": "🦋", "one_in": 67654, "rarity": 67654, "odds": "67,654", "color": (203, 163, 233)},
    {"id": "🐝", "name": "🐝", "one_in": 82392, "rarity": 82392, "odds": "82,392", "color": (73, 93, 213)},
    {"id": "🦊", "name": "🦊", "one_in": 100339, "rarity": 100339, "odds": "100,339", "color": (166, 96, 136)},
    {"id": "🐼", "name": "🐼", "one_in": 122197, "rarity": 122197, "odds": "122,197", "color": (140, 190, 160)},
    {"id": "🐨", "name": "🐨", "one_in": 148815, "rarity": 148815, "odds": "148,815", "color": (120, 110, 90)},
    {"id": "🦁", "name": "🦁", "one_in": 181232, "rarity": 181232, "odds": "181,232", "color": (193, 213, 113)},
    {"id": "🐯", "name": "🐯", "one_in": 220711, "rarity": 220711, "odds": "220,711", "color": (199, 219, 89)},
    {"id": "🐸", "name": "🐸", "one_in": 268789, "rarity": 268789, "odds": "268,789", "color": (172, 102, 112)},
    {"id": "🐙", "name": "🐙", "one_in": 327341, "rarity": 327341, "odds": "327,341", "color": (105, 185, 165)},
    {"id": "🦈", "name": "🦈", "one_in": 398647, "rarity": 398647, "odds": "398,647", "color": (92, 142, 112)},
    {"id": "🐳", "name": "🐳", "one_in": 485486, "rarity": 485486, "odds": "485,486", "color": (167, 127, 137)},
    {"id": "🦅", "name": "🦅", "one_in": 591241, "rarity": 591241, "odds": "591,241", "color": (161, 121, 161)},
    {"id": "🦉", "name": "🦉", "one_in": 720034, "rarity": 720034, "odds": "720,034", "color": (129, 209, 209)},
    {"id": "🌵", "name": "🌵", "one_in": 876882, "rarity": 876882, "odds": "876,882", "color": (129, 209, 149)},
    {"id": "🌋", "name": "🌋", "one_in": 1067897, "rarity": 1067897, "odds": "1,067,897", "color": (195, 95, 155)},
    {"id": "🌊", "name": "🌊", "one_in": 1300522, "rarity": 1300522, "odds": "1,300,522", "color": (158, 208, 228)},
    {"id": "🍎", "name": "🍎", "one_in": 1583820, "rarity": 1583820, "odds": "1,583,820", "color": (154, 84, 194)},
    {"id": "🍒", "name": "🍒", "one_in": 1928830, "rarity": 1928830, "odds": "1,928,830", "color": (122, 172, 72)},
    {"id": "🍇", "name": "🍇", "one_in": 2348995, "rarity": 2348995, "odds": "2,348,995", "color": (75, 155, 195)},
    {"id": "🍓", "name": "🍓", "one_in": 2860686, "rarity": 2860686, "odds": "2,860,686", "color": (159, 59, 169)},
    {"id": "🍕", "name": "🍕", "one_in": 3483841, "rarity": 3483841, "odds": "3,483,841", "color": (233, 193, 193)},
    {"id": "🍩", "name": "🍩", "one_in": 4242741, "rarity": 4242741, "odds": "4,242,741", "color": (73, 93, 93)},
    {"id": "🎂", "name": "🎂", "one_in": 5166955, "rarity": 5166955, "odds": "5,166,955", "color": (98, 148, 138)},
    {"id": "⚽", "name": "⚽", "one_in": 6292495, "rarity": 6292495, "odds": "6,292,495", "color": (149, 109, 159)},
    {"id": "🏀", "name": "🏀", "one_in": 7663215, "rarity": 7663215, "odds": "7,663,215", "color": (232, 162, 202)},
    {"id": "🎮", "name": "🎮", "one_in": 9332526, "rarity": 9332526, "odds": "9,332,526", "color": (106, 216, 156)},
    {"id": "🚀", "name": "🚀", "one_in": 11365469, "rarity": 11365469, "odds": "11,365,469", "color": (180, 170, 150)},
    {"id": "🪐", "name": "🪐", "one_in": 13841257, "rarity": 13841257, "odds": "13,841,257", "color": (140, 190, 220)},
    {"id": "💫", "name": "💫", "one_in": 16856355, "rarity": 16856355, "odds": "16,856,355", "color": (107, 67, 217)},
    {"id": "🔮", "name": "🔮", "one_in": 20528246, "rarity": 20528246, "odds": "20,528,246", "color": (94, 204, 174)},
    {"id": "💍", "name": "💍", "one_in": 25000000, "rarity": 25000000, "odds": "25,000,000", "color": (77, 217, 197)},
    {"id": "yin yang", "name": "yin yang", "one_in": 5000005, "rarity": 5000005, "odds": "5,000,005", "color": (230, 230, 230)},
    {"id": "fulgurite", "name": "fulgurite", "one_in": 30000000, "rarity": 30000000, "odds": "30,000,000", "color": (210, 180, 120)},
    {"id": "kintsugi", "name": "kintsugi", "one_in": 36653550, "rarity": 36653550, "odds": "36,653,550", "color": (212, 175, 55)},
    {"id": "orrery", "name": "orrery", "one_in": 44782760, "rarity": 44782760, "odds": "44,782,760", "color": (180, 160, 110)},
    {"id": "antikythera", "name": "antikythera", "one_in": 54715000, "rarity": 54715000, "odds": "54,715,000", "color": (150, 140, 100)},
    {"id": "astrolabe", "name": "astrolabe", "one_in": 66850000, "rarity": 66850000, "odds": "66,850,000", "color": (196, 160, 70)},
    {"id": "fluorite", "name": "fluorite", "one_in": 81680000, "rarity": 81680000, "odds": "81,680,000", "color": (120, 90, 200)},
    {"id": "nautilus", "name": "nautilus", "one_in": 99800000, "rarity": 99800000, "odds": "99,800,000", "color": (230, 200, 160)},
    {"id": "lodestone", "name": "lodestone", "one_in": 121930000, "rarity": 121930000, "odds": "121,930,000", "color": (90, 90, 100)},
    {"id": "mycelium", "name": "mycelium", "one_in": 148970000, "rarity": 148970000, "odds": "148,970,000", "color": (170, 150, 110)},
    {"id": "bioluminescence", "name": "bioluminescence", "one_in": 182010000, "rarity": 182010000, "odds": "182,010,000", "color": (40, 220, 180)},
    {"id": "kaleidoscope", "name": "kaleidoscope", "one_in": 222370000, "rarity": 222370000, "odds": "222,370,000", "color": (220, 80, 160)},
    {"id": "sundial", "name": "sundial", "one_in": 271690000, "rarity": 271690000, "odds": "271,690,000", "color": (190, 160, 90)},
    {"id": "copal", "name": "copal", "one_in": 331950000, "rarity": 331950000, "odds": "331,950,000", "color": (210, 140, 40)},
    {"id": "tesla", "name": "tesla", "one_in": 405570000, "rarity": 405570000, "odds": "405,570,000", "color": (120, 180, 255)},
    {"id": "dichroic", "name": "dichroic", "one_in": 495520000, "rarity": 495520000, "odds": "495,520,000", "color": (80, 200, 220)},
    {"id": "jet", "name": "jet", "one_in": 605420000, "rarity": 605420000, "odds": "605,420,000", "color": (40, 40, 48)},
    {"id": "brinicle", "name": "brinicle", "one_in": 739690000, "rarity": 739690000, "odds": "739,690,000", "color": (140, 200, 230)},
    {"id": "lenticular", "name": "lenticular", "one_in": 903740000, "rarity": 903740000, "odds": "903,740,000", "color": (180, 190, 210)},
    {"id": "mammatus", "name": "mammatus", "one_in": 1104200000, "rarity": 1104200000, "odds": "1,104,200,000", "color": (120, 110, 140)},
    {"id": "catatumbo", "name": "catatumbo", "one_in": 1349100000, "rarity": 1349100000, "odds": "1,349,100,000", "color": (180, 170, 80)},
    {"id": "sailing stone", "name": "sailing stone", "one_in": 1648300000, "rarity": 1648300000, "odds": "1,648,300,000", "color": (160, 140, 110)},
    {"id": "blood falls", "name": "blood falls", "one_in": 2013900000, "rarity": 2013900000, "odds": "2,013,900,000", "color": (180, 40, 40)},
    {"id": "darvaza", "name": "darvaza", "one_in": 2460500000, "rarity": 2460500000, "odds": "2,460,500,000", "color": (255, 80, 20)},
    {"id": "richat", "name": "richat", "one_in": 3006200000, "rarity": 3006200000, "odds": "3,006,200,000", "color": (190, 150, 80)},
    {"id": "socotra", "name": "socotra", "one_in": 3672900000, "rarity": 3672900000, "odds": "3,672,900,000", "color": (80, 140, 70)},
    {"id": "hoag", "name": "hoag", "one_in": 4487500000, "rarity": 4487500000, "odds": "4,487,500,000", "color": (160, 180, 230)},
    {"id": "crab nebula", "name": "crab nebula", "one_in": 5482800000, "rarity": 5482800000, "odds": "5,482,800,000", "color": (180, 140, 200)},
    {"id": "pillars", "name": "pillars", "one_in": 6698800000, "rarity": 6698800000, "odds": "6,698,800,000", "color": (140, 120, 160)},
    {"id": "cartwheel", "name": "cartwheel", "one_in": 8184700000, "rarity": 8184700000, "odds": "8,184,700,000", "color": (200, 180, 140)},
    {"id": "heat death", "name": "heat death", "one_in": 10000000000, "rarity": 10000000000, "odds": "10,000,000,000", "color": (80, 40, 50)},
    {"id": "honey", "name": "honey", "one_in": 18, "rarity": 18, "odds": "18", "color": (212, 150, 40)},
    {"id": "candle", "name": "candle", "one_in": 21, "rarity": 21, "odds": "21", "color": (255, 190, 80)},
    {"id": "pillow", "name": "pillow", "one_in": 24, "rarity": 24, "odds": "24", "color": (230, 220, 210)},
    {"id": "kettle", "name": "kettle", "one_in": 28, "rarity": 28, "odds": "28", "color": (180, 190, 200)},
    {"id": "spoon", "name": "spoon", "one_in": 32, "rarity": 32, "odds": "32", "color": (200, 200, 205)},
    {"id": "blanket", "name": "blanket", "one_in": 37, "rarity": 37, "odds": "37", "color": (180, 140, 120)},
    {"id": "button", "name": "button", "one_in": 43, "rarity": 43, "odds": "43", "color": (220, 220, 230)},
    {"id": "ladder", "name": "ladder", "one_in": 49, "rarity": 49, "odds": "49", "color": (170, 120, 70)},
    {"id": "bucket", "name": "bucket", "one_in": 57, "rarity": 57, "odds": "57", "color": (160, 165, 170)},
    {"id": "ribbon", "name": "ribbon", "one_in": 66, "rarity": 66, "odds": "66", "color": (200, 40, 50)},
    {"id": "yarn", "name": "yarn", "one_in": 76, "rarity": 76, "odds": "76", "color": (200, 80, 90)},
    {"id": "cookie", "name": "cookie", "one_in": 88, "rarity": 88, "odds": "88", "color": (190, 130, 70)},
    {"id": "mitten", "name": "mitten", "one_in": 102, "rarity": 102, "odds": "102", "color": (180, 50, 60)},
    {"id": "lantern", "name": "lantern", "one_in": 118, "rarity": 118, "odds": "118", "color": (255, 170, 60)},
    {"id": "mug", "name": "mug", "one_in": 136, "rarity": 136, "odds": "136", "color": (210, 200, 190)},
    {"id": "basket", "name": "basket", "one_in": 157, "rarity": 157, "odds": "157", "color": (170, 120, 60)},
    {"id": "soap", "name": "soap", "one_in": 182, "rarity": 182, "odds": "182", "color": (230, 230, 220)},
    {"id": "towel", "name": "towel", "one_in": 210, "rarity": 210, "odds": "210", "color": (200, 210, 220)},
    {"id": "hammer", "name": "hammer", "one_in": 242, "rarity": 242, "odds": "242", "color": (140, 140, 145)},
    {"id": "scarf", "name": "scarf", "one_in": 280, "rarity": 280, "odds": "280", "color": (180, 50, 70)},
    {"id": "doge", "name": "doge", "one_in": 700, "rarity": 700, "odds": "700", "color": (210, 170, 90)},
    {"id": "grumpy", "name": "grumpy", "one_in": 850, "rarity": 850, "odds": "850", "color": (80, 80, 90)},
    {"id": "harambe", "name": "harambe", "one_in": 1032, "rarity": 1032, "odds": "1,032", "color": (60, 60, 60)},
    {"id": "stonks", "name": "stonks", "one_in": 1253, "rarity": 1253, "odds": "1,253", "color": (40, 180, 80)},
    {"id": "nyan", "name": "nyan", "one_in": 1522, "rarity": 1522, "odds": "1,522", "color": (255, 120, 180)},
    {"id": "coffin dance", "name": "coffin dance", "one_in": 1848, "rarity": 1848, "odds": "1,848", "color": (40, 40, 50)},
    {"id": "skibidi", "name": "skibidi", "one_in": 2244, "rarity": 2244, "odds": "2,244", "color": (230, 230, 235)},
    {"id": "sigma", "name": "sigma", "one_in": 2725, "rarity": 2725, "odds": "2,725", "color": (90, 100, 120)},
    {"id": "ohio", "name": "ohio", "one_in": 3309, "rarity": 3309, "odds": "3,309", "color": (180, 30, 40)},
    {"id": "gigachad", "name": "gigachad", "one_in": 4018, "rarity": 4018, "odds": "4,018", "color": (180, 180, 190)},
    {"id": "npc", "name": "npc", "one_in": 4879, "rarity": 4879, "odds": "4,879", "color": (210, 190, 170)},
    {"id": "copium", "name": "copium", "one_in": 5924, "rarity": 5924, "odds": "5,924", "color": (80, 160, 200)},
    {"id": "rizz", "name": "rizz", "one_in": 7193, "rarity": 7193, "odds": "7,193", "color": (200, 30, 50)},
    {"id": "cheems", "name": "cheems", "one_in": 8735, "rarity": 8735, "odds": "8,735", "color": (190, 160, 110)},
    {"id": "bonk", "name": "bonk", "one_in": 10606, "rarity": 10606, "odds": "10,606", "color": (160, 110, 60)},
    {"id": "yeet", "name": "yeet", "one_in": 12879, "rarity": 12879, "odds": "12,879", "color": (70, 140, 220)},
    {"id": "bussin", "name": "bussin", "one_in": 15639, "rarity": 15639, "odds": "15,639", "color": (200, 120, 50)},
    {"id": "monke", "name": "monke", "one_in": 18990, "rarity": 18990, "odds": "18,990", "color": (140, 100, 60)},
    {"id": "bingus", "name": "bingus", "one_in": 23059, "rarity": 23059, "odds": "23,059", "color": (200, 170, 150)},
    {"id": "sus", "name": "sus", "one_in": 28000, "rarity": 28000, "odds": "28,000", "color": (220, 40, 40)},
    {"id": "mario", "name": "mario", "one_in": 50000, "rarity": 50000, "odds": "50,000", "color": (220, 30, 40)},
    {"id": "pikachu", "name": "pikachu", "one_in": 58215, "rarity": 58215, "odds": "58,215", "color": (240, 200, 40)},
    {"id": "lightsaber", "name": "lightsaber", "one_in": 67780, "rarity": 67780, "odds": "67,780", "color": (80, 220, 255)},
    {"id": "grogu", "name": "grogu", "one_in": 78917, "rarity": 78917, "odds": "78,917", "color": (120, 160, 90)},
    {"id": "shrek", "name": "shrek", "one_in": 91884, "rarity": 91884, "odds": "91,884", "color": (90, 160, 50)},
    {"id": "spongebob", "name": "spongebob", "one_in": 106981, "rarity": 106981, "odds": "106,981", "color": (240, 210, 60)},
    {"id": "barbie", "name": "barbie", "one_in": 124558, "rarity": 124558, "odds": "124,558", "color": (230, 80, 140)},
    {"id": "goku", "name": "goku", "one_in": 145024, "rarity": 145024, "odds": "145,024", "color": (240, 140, 30)},
    {"id": "naruto", "name": "naruto", "one_in": 168852, "rarity": 168852, "odds": "168,852", "color": (240, 140, 40)},
    {"id": "luffy", "name": "luffy", "one_in": 196595, "rarity": 196595, "odds": "196,595", "color": (220, 50, 40)},
    {"id": "gauntlet", "name": "gauntlet", "one_in": 228897, "rarity": 228897, "odds": "228,897", "color": (190, 150, 50)},
    {"id": "joker", "name": "joker", "one_in": 266506, "rarity": 266506, "odds": "266,506", "color": (80, 160, 60)},
    {"id": "elsa", "name": "elsa", "one_in": 310294, "rarity": 310294, "odds": "310,294", "color": (140, 200, 240)},
    {"id": "kirby", "name": "kirby", "one_in": 361277, "rarity": 361277, "odds": "361,277", "color": (240, 140, 180)},
    {"id": "yoda", "name": "yoda", "one_in": 420637, "rarity": 420637, "odds": "420,637", "color": (120, 150, 80)},
    {"id": "heisenberg", "name": "heisenberg", "one_in": 489750, "rarity": 489750, "odds": "489,750", "color": (40, 50, 40)},
    {"id": "squid game", "name": "squid game", "one_in": 570219, "rarity": 570219, "odds": "570,219", "color": (220, 40, 80)},
    {"id": "matrix", "name": "matrix", "one_in": 663909, "rarity": 663909, "odds": "663,909", "color": (40, 220, 70)},
    {"id": "tron", "name": "tron", "one_in": 772993, "rarity": 772993, "odds": "772,993", "color": (40, 180, 255)},
    {"id": "totoro", "name": "totoro", "one_in": 900000, "rarity": 900000, "odds": "900,000", "color": (140, 140, 150)},
    {"id": "tardigrade", "name": "tardigrade", "one_in": 1500000, "rarity": 1500000, "odds": "1,500,000", "color": (180, 140, 100)},
    {"id": "stromatolite", "name": "stromatolite", "one_in": 1770476, "rarity": 1770476, "odds": "1,770,476", "color": (140, 120, 90)},
    {"id": "quasicrystal", "name": "quasicrystal", "one_in": 2089723, "rarity": 2089723, "odds": "2,089,723", "color": (180, 190, 210)},
    {"id": "tokamak", "name": "tokamak", "one_in": 2466537, "rarity": 2466537, "odds": "2,466,537", "color": (80, 140, 200)},
    {"id": "mobius", "name": "mobius", "one_in": 2911296, "rarity": 2911296, "odds": "2,911,296", "color": (200, 200, 210)},
    {"id": "klein bottle", "name": "klein bottle", "one_in": 3436253, "rarity": 3436253, "odds": "3,436,253", "color": (180, 200, 220)},
    {"id": "mandelbrot", "name": "mandelbrot", "one_in": 4055869, "rarity": 4055869, "odds": "4,055,869", "color": (20, 20, 80)},
    {"id": "cenote", "name": "cenote", "one_in": 4787213, "rarity": 4787213, "odds": "4,787,213", "color": (40, 160, 170)},
    {"id": "inselberg", "name": "inselberg", "one_in": 5650430, "rarity": 5650430, "odds": "5,650,430", "color": (170, 130, 90)},
    {"id": "yardang", "name": "yardang", "one_in": 6669300, "rarity": 6669300, "odds": "6,669,300", "color": (190, 160, 110)},
    {"id": "penitentes", "name": "penitentes", "one_in": 7871890, "rarity": 7871890, "odds": "7,871,890", "color": (200, 220, 230)},
    {"id": "sastrugi", "name": "sastrugi", "one_in": 9291329, "rarity": 9291329, "odds": "9,291,329", "color": (210, 220, 230)},
    {"id": "frost flower", "name": "frost flower", "one_in": 10966716, "rarity": 10966716, "odds": "10,966,716", "color": (220, 230, 240)},
    {"id": "brocken", "name": "brocken", "one_in": 12944205, "rarity": 12944205, "odds": "12,944,205", "color": (160, 160, 170)},
    {"id": "moonbow", "name": "moonbow", "one_in": 15278269, "rarity": 15278269, "odds": "15,278,269", "color": (180, 180, 210)},
    {"id": "parhelion", "name": "parhelion", "one_in": 18033205, "rarity": 18033205, "odds": "18,033,205", "color": (230, 200, 140)},
    {"id": "asperitas", "name": "asperitas", "one_in": 21284905, "rarity": 21284905, "odds": "21,284,905", "color": (90, 100, 120)},
    {"id": "noctilucent", "name": "noctilucent", "one_in": 25122942, "rarity": 25122942, "odds": "25,122,942", "color": (80, 140, 200)},
    {"id": "haboob", "name": "haboob", "one_in": 29653043, "rarity": 29653043, "odds": "29,653,043", "color": (180, 140, 80)},
    {"id": "supercell", "name": "supercell", "one_in": 35000000, "rarity": 35000000, "odds": "35,000,000", "color": (70, 80, 110)},
    {"id": "finally", "name": "finally", "one_in": 100000000000, "rarity": 100000000000, "odds": "100,000,000,000", "color": (255, 230, 160)},
    {"id": "aftermath", "name": "aftermath", "one_in": 1000000000000, "rarity": 1000000000000, "odds": "1,000,000,000,000", "color": (90, 90, 95)},
    {"id": "ending", "name": "ending", "one_in": 1000000000000000000, "rarity": 1000000000000000000, "odds": "1,000,000,000,000,000,000", "color": (20, 10, 30)},
    {"id": "regan", "name": "regan", "one_in": 2500, "rarity": 2500, "odds": "2,500", "color": (120, 100, 70)},
    {"id": "pencil", "name": "pencil", "one_in": 36, "rarity": 36, "odds": "36", "color": (240, 200, 40)},
    {"id": "pen", "name": "pen", "one_in": 44, "rarity": 44, "odds": "44", "color": (30, 70, 160)},
    {"id": "eraser", "name": "eraser", "one_in": 52, "rarity": 52, "odds": "52", "color": (230, 140, 160)},
    {"id": "notebook", "name": "notebook", "one_in": 68, "rarity": 68, "odds": "68", "color": (40, 90, 160)},
    {"id": "ruler", "name": "ruler", "one_in": 84, "rarity": 84, "odds": "84", "color": (210, 180, 80)},
    {"id": "crayon", "name": "crayon", "one_in": 108, "rarity": 108, "odds": "108", "color": (220, 60, 50)},
    {"id": "marker", "name": "marker", "one_in": 132, "rarity": 132, "odds": "132", "color": (20, 20, 20)},
    {"id": "stapler", "name": "stapler", "one_in": 168, "rarity": 168, "odds": "168", "color": (40, 40, 45)},
    {"id": "scissors", "name": "scissors", "one_in": 210, "rarity": 210, "odds": "210", "color": (170, 175, 180)},
    {"id": "glue", "name": "glue", "one_in": 260, "rarity": 260, "odds": "260", "color": (230, 230, 220)},
    {"id": "fork", "name": "fork", "one_in": 24, "rarity": 24, "odds": "24", "color": (190, 190, 195)},
    {"id": "plate", "name": "plate", "one_in": 30, "rarity": 30, "odds": "30", "color": (230, 230, 225)},
    {"id": "bowl", "name": "bowl", "one_in": 38, "rarity": 38, "odds": "38", "color": (210, 200, 185)},
    {"id": "cup", "name": "cup", "one_in": 48, "rarity": 48, "odds": "48", "color": (230, 230, 230)},
    {"id": "straw", "name": "straw", "one_in": 60, "rarity": 60, "odds": "60", "color": (220, 180, 60)},
    {"id": "napkin", "name": "napkin", "one_in": 76, "rarity": 76, "odds": "76", "color": (235, 230, 220)},
    {"id": "sponge", "name": "sponge", "one_in": 96, "rarity": 96, "odds": "96", "color": (220, 190, 50)},
    {"id": "toothbrush", "name": "toothbrush", "one_in": 120, "rarity": 120, "odds": "120", "color": (80, 160, 220)},
    {"id": "toothpaste", "name": "toothpaste", "one_in": 150, "rarity": 150, "odds": "150", "color": (40, 140, 200)},
    {"id": "comb", "name": "comb", "one_in": 190, "rarity": 190, "odds": "190", "color": (40, 40, 45)},
    {"id": "brush", "name": "brush", "one_in": 240, "rarity": 240, "odds": "240", "color": (160, 90, 50)},
    {"id": "mirror", "name": "mirror", "one_in": 300, "rarity": 300, "odds": "300", "color": (180, 190, 200)},
    {"id": "clock", "name": "clock", "one_in": 380, "rarity": 380, "odds": "380", "color": (40, 40, 50)},
    {"id": "lamp", "name": "lamp", "one_in": 480, "rarity": 480, "odds": "480", "color": (230, 190, 80)},
    {"id": "chair", "name": "chair", "one_in": 600, "rarity": 600, "odds": "600", "color": (140, 90, 50)},
    {"id": "table", "name": "table", "one_in": 760, "rarity": 760, "odds": "760", "color": (150, 100, 55)},
    {"id": "door", "name": "door", "one_in": 960, "rarity": 960, "odds": "960", "color": (120, 75, 40)},
    {"id": "window", "name": "window", "one_in": 1200, "rarity": 1200, "odds": "1,200", "color": (160, 190, 210)},
    {"id": "shoe", "name": "shoe", "one_in": 1500, "rarity": 1500, "odds": "1,500", "color": (40, 40, 50)},
    {"id": "sock", "name": "sock", "one_in": 1900, "rarity": 1900, "odds": "1,900", "color": (180, 180, 190)},
    {"id": "banana", "name": "banana", "one_in": 2400, "rarity": 2400, "odds": "2,400", "color": (240, 200, 40)},
    {"id": "bread", "name": "bread", "one_in": 3000, "rarity": 3000, "odds": "3,000", "color": (190, 140, 70)},
    {"id": "sandwich", "name": "sandwich", "one_in": 3800, "rarity": 3800, "odds": "3,800", "color": (200, 160, 80)},
    {"id": "cheese", "name": "cheese", "one_in": 4800, "rarity": 4800, "odds": "4,800", "color": (240, 190, 40)},
    {"id": "egg", "name": "egg", "one_in": 6000, "rarity": 6000, "odds": "6,000", "color": (235, 225, 200)},
    {"id": "milk", "name": "milk", "one_in": 7600, "rarity": 7600, "odds": "7,600", "color": (240, 240, 240)},
    {"id": "cereal", "name": "cereal", "one_in": 9600, "rarity": 9600, "odds": "9,600", "color": (200, 150, 60)},
    {"id": "waffle", "name": "waffle", "one_in": 12000, "rarity": 12000, "odds": "12,000", "color": (190, 130, 50)},
    {"id": "pancake", "name": "pancake", "one_in": 15000, "rarity": 15000, "odds": "15,000", "color": (210, 160, 70)},
    {"id": "pretzel", "name": "pretzel", "one_in": 19000, "rarity": 19000, "odds": "19,000", "color": (170, 110, 50)},
    {"id": "bagel", "name": "bagel", "one_in": 24000, "rarity": 24000, "odds": "24,000", "color": (190, 140, 70)},
    {"id": "taco", "name": "taco", "one_in": 30000, "rarity": 30000, "odds": "30,000", "color": (210, 150, 40)},
    {"id": "burger", "name": "burger", "one_in": 38000, "rarity": 38000, "odds": "38,000", "color": (140, 80, 40)},
    {"id": "fries", "name": "fries", "one_in": 48000, "rarity": 48000, "odds": "48,000", "color": (230, 180, 50)},
    {"id": "sushi", "name": "sushi", "one_in": 60000, "rarity": 60000, "odds": "60,000", "color": (220, 80, 70)},
    {"id": "rabbit", "name": "rabbit", "one_in": 76000, "rarity": 76000, "odds": "76,000", "color": (180, 170, 160)},
    {"id": "horse", "name": "horse", "one_in": 96000, "rarity": 96000, "odds": "96,000", "color": (140, 90, 50)},
    {"id": "cow", "name": "cow", "one_in": 120000, "rarity": 120000, "odds": "120,000", "color": (40, 40, 40)},
    {"id": "pig", "name": "pig", "one_in": 150000, "rarity": 150000, "odds": "150,000", "color": (230, 160, 160)},
    {"id": "sheep", "name": "sheep", "one_in": 190000, "rarity": 190000, "odds": "190,000", "color": (220, 220, 220)},
    {"id": "duck", "name": "duck", "one_in": 240000, "rarity": 240000, "odds": "240,000", "color": (40, 120, 70)},
    {"id": "penguin", "name": "penguin", "one_in": 300000, "rarity": 300000, "odds": "300,000", "color": (20, 20, 30)},
    {"id": "bear", "name": "bear", "one_in": 380000, "rarity": 380000, "odds": "380,000", "color": (110, 70, 40)},
    {"id": "wolf", "name": "wolf", "one_in": 480000, "rarity": 480000, "odds": "480,000", "color": (90, 90, 95)},
    {"id": "deer", "name": "deer", "one_in": 600000, "rarity": 600000, "odds": "600,000", "color": (140, 100, 60)},
    {"id": "turtle", "name": "turtle", "one_in": 760000, "rarity": 760000, "odds": "760,000", "color": (40, 120, 70)},
    {"id": "snake", "name": "snake", "one_in": 960000, "rarity": 960000, "odds": "960,000", "color": (50, 110, 50)},
    {"id": "parrot", "name": "parrot", "one_in": 1200000, "rarity": 1200000, "odds": "1,200,000", "color": (40, 160, 80)},
    {"id": "hamster", "name": "hamster", "one_in": 1500000, "rarity": 1500000, "odds": "1,500,000", "color": (190, 140, 80)},
    {"id": "otter", "name": "otter", "one_in": 1900000, "rarity": 1900000, "odds": "1,900,000", "color": (110, 80, 50)},
    {"id": "kermit", "name": "kermit", "one_in": 2400000, "rarity": 2400000, "odds": "2,400,000", "color": (60, 170, 60)},
    {"id": "elmo", "name": "elmo", "one_in": 3000000, "rarity": 3000000, "odds": "3,000,000", "color": (220, 40, 40)},
    {"id": "minion", "name": "minion", "one_in": 3800000, "rarity": 3800000, "odds": "3,800,000", "color": (230, 190, 30)},
    {"id": "sonic", "name": "sonic", "one_in": 4800000, "rarity": 4800000, "odds": "4,800,000", "color": (30, 90, 210)},
    {"id": "vader", "name": "vader", "one_in": 6000000, "rarity": 6000000, "odds": "6,000,000", "color": (20, 20, 25)},
    {"id": "homer", "name": "homer", "one_in": 7600000, "rarity": 7600000, "odds": "7,600,000", "color": (240, 200, 60)},
    {"id": "squidward", "name": "squidward", "one_in": 9600000, "rarity": 9600000, "odds": "9,600,000", "color": (120, 170, 140)},
    {"id": "patrick", "name": "patrick", "one_in": 12000000, "rarity": 12000000, "odds": "12,000,000", "color": (230, 140, 150)},
    {"id": "lighthouse", "name": "lighthouse", "one_in": 15000000, "rarity": 15000000, "odds": "15,000,000", "color": (230, 230, 230)},
    {"id": "shaggy", "name": "shaggy", "one_in": 19000000, "rarity": 19000000, "odds": "19,000,000", "color": (80, 140, 60)},
    {"id": "everest", "name": "everest", "one_in": 24000000, "rarity": 24000000, "odds": "24,000,000", "color": (200, 210, 220)},
    {"id": "fuji", "name": "fuji", "one_in": 30000000, "rarity": 30000000, "odds": "30,000,000", "color": (180, 190, 200)},
    {"id": "niagara", "name": "niagara", "one_in": 38000000, "rarity": 38000000, "odds": "38,000,000", "color": (80, 160, 200)},
    {"id": "sahara", "name": "sahara", "one_in": 48000000, "rarity": 48000000, "odds": "48,000,000", "color": (210, 170, 90)},
    {"id": "glacier", "name": "glacier", "one_in": 60000000, "rarity": 60000000, "odds": "60,000,000", "color": (180, 210, 220)},
    {"id": "geyser", "name": "geyser", "one_in": 76000000, "rarity": 76000000, "odds": "76,000,000", "color": (180, 200, 210)},
    {"id": "fjord", "name": "fjord", "one_in": 96000000, "rarity": 96000000, "odds": "96,000,000", "color": (70, 120, 150)},
    {"id": "canyon", "name": "canyon", "one_in": 120000000, "rarity": 120000000, "odds": "120,000,000", "color": (180, 90, 50)},
    {"id": "reef", "name": "reef", "one_in": 150000000, "rarity": 150000000, "odds": "150,000,000", "color": (40, 140, 160)},
    {"id": "iceberg", "name": "iceberg", "one_in": 190000000, "rarity": 190000000, "odds": "190,000,000", "color": (200, 220, 230)},
    {"id": "waterfall", "name": "waterfall", "one_in": 19198, "rarity": 19198, "odds": "19,198", "color": (80, 160, 200)},
    {"id": "volcano", "name": "volcano", "one_in": 20936, "rarity": 20936, "odds": "20,936", "color": (180, 60, 30)},
    {"id": "pyramid", "name": "pyramid", "one_in": 22830, "rarity": 22830, "odds": "22,830", "color": (210, 180, 120)},
    {"id": "castle", "name": "castle", "one_in": 24897, "rarity": 24897, "odds": "24,897", "color": (120, 120, 130)},
    {"id": "colosseum", "name": "colosseum", "one_in": 27150, "rarity": 27150, "odds": "27,150", "color": (180, 150, 110)},
    {"id": "rainforest", "name": "rainforest", "one_in": 29607, "rarity": 29607, "odds": "29,607", "color": (30, 120, 50)},
    {"id": "redwood", "name": "redwood", "one_in": 32287, "rarity": 32287, "odds": "32,287", "color": (90, 50, 30)},
    {"id": "baobab", "name": "baobab", "one_in": 35209, "rarity": 35209, "odds": "35,209", "color": (160, 120, 70)},
    {"id": "mangrove", "name": "mangrove", "one_in": 38396, "rarity": 38396, "odds": "38,396", "color": (40, 110, 80)},
    {"id": "sequoia", "name": "sequoia", "one_in": 41871, "rarity": 41871, "odds": "41,871", "color": (80, 50, 30)},
    {"id": "axolotl", "name": "axolotl", "one_in": 45661, "rarity": 45661, "odds": "45,661", "color": (220, 140, 160)},
    {"id": "pangolin", "name": "pangolin", "one_in": 49793, "rarity": 49793, "odds": "49,793", "color": (140, 100, 60)},
    {"id": "okapi", "name": "okapi", "one_in": 54300, "rarity": 54300, "odds": "54,300", "color": (120, 70, 40)},
    {"id": "narwhal", "name": "narwhal", "one_in": 59215, "rarity": 59215, "odds": "59,215", "color": (170, 190, 200)},
    {"id": "quokka", "name": "quokka", "one_in": 64574, "rarity": 64574, "odds": "64,574", "color": (140, 100, 60)},
    {"id": "platypus", "name": "platypus", "one_in": 70419, "rarity": 70419, "odds": "70,419", "color": (110, 80, 50)},
    {"id": "kakapo", "name": "kakapo", "one_in": 76792, "rarity": 76792, "odds": "76,792", "color": (70, 120, 60)},
    {"id": "chameleon", "name": "chameleon", "one_in": 83742, "rarity": 83742, "odds": "83,742", "color": (40, 140, 60)},
    {"id": "jaguar", "name": "jaguar", "one_in": 91322, "rarity": 91322, "odds": "91,322", "color": (180, 130, 50)},
    {"id": "leopard", "name": "leopard", "one_in": 99587, "rarity": 99587, "odds": "99,587", "color": (190, 150, 70)},
    {"id": "gorilla", "name": "gorilla", "one_in": 108600, "rarity": 108600, "odds": "108,600", "color": (50, 50, 50)},
    {"id": "elephant", "name": "elephant", "one_in": 118429, "rarity": 118429, "odds": "118,429", "color": (140, 140, 145)},
    {"id": "whale", "name": "whale", "one_in": 129148, "rarity": 129148, "odds": "129,148", "color": (40, 80, 120)},
    {"id": "dolphin", "name": "dolphin", "one_in": 140837, "rarity": 140837, "odds": "140,837", "color": (80, 150, 190)},
    {"id": "flamingo", "name": "flamingo", "one_in": 153584, "rarity": 153584, "odds": "153,584", "color": (230, 120, 150)},
    {"id": "magnetar", "name": "magnetar", "one_in": 191980, "rarity": 191980, "odds": "191,980", "color": (40, 40, 80)},
    {"id": "andromeda", "name": "andromeda", "one_in": 209356, "rarity": 209356, "odds": "209,356", "color": (80, 90, 160)},
    {"id": "milkyway", "name": "milkyway", "one_in": 228304, "rarity": 228304, "odds": "228,304", "color": (20, 20, 50)},
    {"id": "meteorite", "name": "meteorite", "one_in": 248967, "rarity": 248967, "odds": "248,967", "color": (80, 70, 65)},
    {"id": "fossil", "name": "fossil", "one_in": 271501, "rarity": 271501, "odds": "271,501", "color": (150, 130, 90)},
    {"id": "trilobite", "name": "trilobite", "one_in": 296074, "rarity": 296074, "odds": "296,074", "color": (120, 100, 70)},
    {"id": "ammonite", "name": "ammonite", "one_in": 322871, "rarity": 322871, "odds": "322,871", "color": (140, 120, 80)},
    {"id": "coelacanth", "name": "coelacanth", "one_in": 352093, "rarity": 352093, "odds": "352,093", "color": (60, 80, 100)},
    {"id": "komodo", "name": "komodo", "one_in": 383960, "rarity": 383960, "odds": "383,960", "color": (90, 100, 50)},
    {"id": "anaconda", "name": "anaconda", "one_in": 418711, "rarity": 418711, "odds": "418,711", "color": (40, 90, 40)},
    {"id": "condor", "name": "condor", "one_in": 456608, "rarity": 456608, "odds": "456,608", "color": (40, 40, 45)},
    {"id": "albatross", "name": "albatross", "one_in": 497934, "rarity": 497934, "odds": "497,934", "color": (200, 200, 205)},
    {"id": "peacock", "name": "peacock", "one_in": 543001, "rarity": 543001, "odds": "543,001", "color": (20, 120, 80)},
    {"id": "macaw", "name": "macaw", "one_in": 592147, "rarity": 592147, "odds": "592,147", "color": (220, 60, 40)},
    {"id": "petra", "name": "petra", "one_in": 645741, "rarity": 645741, "odds": "645,741", "color": (180, 90, 60)},
    {"id": "stonehenge", "name": "stonehenge", "one_in": 704186, "rarity": 704186, "odds": "704,186", "color": (140, 140, 130)},
    {"id": "easter island", "name": "easter island", "one_in": 767920, "rarity": 767920, "odds": "767,920", "color": (120, 110, 90)},
    {"id": "machu picchu", "name": "machu picchu", "one_in": 837423, "rarity": 837423, "odds": "837,423", "color": (80, 140, 70)},
    {"id": "taj mahal", "name": "taj mahal", "one_in": 913216, "rarity": 913216, "odds": "913,216", "color": (230, 230, 235)},
    {"id": "angkor", "name": "angkor", "one_in": 995869, "rarity": 995869, "odds": "995,869", "color": (160, 120, 70)},
    {"id": "hubble", "name": "hubble", "one_in": 1086003, "rarity": 1086003, "odds": "1,086,003", "color": (180, 180, 190)},
    {"id": "apollo", "name": "apollo", "one_in": 1184294, "rarity": 1184294, "odds": "1,184,294", "color": (200, 200, 205)},
    {"id": "observatory", "name": "observatory", "one_in": 1291482, "rarity": 1291482, "odds": "1,291,482", "color": (40, 50, 80)},
    {"id": "telescope", "name": "telescope", "one_in": 1408371, "rarity": 1408371, "odds": "1,408,371", "color": (160, 160, 170)},
    {"id": "blue whale", "name": "blue whale", "one_in": 1535840, "rarity": 1535840, "odds": "1,535,840", "color": (50, 90, 140)},
    {"id": "apron", "name": "apron", "one_in": 42, "rarity": 42, "odds": "42", "color": (40, 207, 66)},
    {"id": "backpack", "name": "backpack", "one_in": 46, "rarity": 46, "odds": "46", "color": (216, 179, 44)},
    {"id": "bandage", "name": "bandage", "one_in": 47, "rarity": 47, "odds": "47", "color": (170, 214, 54)},
    {"id": "battery", "name": "battery", "one_in": 50, "rarity": 50, "odds": "50", "color": (67, 66, 172)},
    {"id": "beanie", "name": "beanie", "one_in": 51, "rarity": 51, "odds": "51", "color": (76, 115, 94)},
    {"id": "belt", "name": "belt", "one_in": 54, "rarity": 54, "odds": "54", "color": (79, 161, 95)},
    {"id": "bicycle", "name": "bicycle", "one_in": 55, "rarity": 55, "odds": "55", "color": (67, 155, 102)},
    {"id": "blender", "name": "blender", "one_in": 56, "rarity": 56, "odds": "56", "color": (100, 65, 66)},
    {"id": "bookmark", "name": "bookmark", "one_in": 58, "rarity": 58, "odds": "58", "color": (190, 74, 150)},
    {"id": "bottle", "name": "bottle", "one_in": 59, "rarity": 59, "odds": "59", "color": (114, 47, 219)},
    {"id": "broom", "name": "broom", "one_in": 62, "rarity": 62, "odds": "62", "color": (167, 53, 85)},
    {"id": "calculator", "name": "calculator", "one_in": 63, "rarity": 63, "odds": "63", "color": (210, 123, 181)},
    {"id": "calendar", "name": "calendar", "one_in": 64, "rarity": 64, "odds": "64", "color": (100, 86, 189)},
    {"id": "camera", "name": "camera", "one_in": 67, "rarity": 67, "odds": "67", "color": (81, 169, 47)},
    {"id": "cardboard", "name": "cardboard", "one_in": 70, "rarity": 70, "odds": "70", "color": (202, 92, 90)},
    {"id": "cassette", "name": "cassette", "one_in": 71, "rarity": 71, "odds": "71", "color": (164, 99, 75)},
    {"id": "charger", "name": "charger", "one_in": 72, "rarity": 72, "odds": "72", "color": (228, 183, 161)},
    {"id": "chopsticks", "name": "chopsticks", "one_in": 74, "rarity": 74, "odds": "74", "color": (67, 180, 129)},
    {"id": "clipboard", "name": "clipboard", "one_in": 75, "rarity": 75, "odds": "75", "color": (56, 71, 96)},
    {"id": "clothespin", "name": "clothespin", "one_in": 78, "rarity": 78, "odds": "78", "color": (161, 49, 169)},
    {"id": "coaster", "name": "coaster", "one_in": 79, "rarity": 79, "odds": "79", "color": (59, 151, 56)},
    {"id": "coffee", "name": "coffee", "one_in": 80, "rarity": 80, "odds": "80", "color": (80, 44, 41)},
    {"id": "colander", "name": "colander", "one_in": 82, "rarity": 82, "odds": "82", "color": (48, 72, 102)},
    {"id": "cork", "name": "cork", "one_in": 83, "rarity": 83, "odds": "83", "color": (57, 88, 96)},
    {"id": "couch", "name": "couch", "one_in": 86, "rarity": 86, "odds": "86", "color": (60, 126, 102)},
    {"id": "dustpan", "name": "dustpan", "one_in": 87, "rarity": 87, "odds": "87", "color": (103, 62, 53)},
    {"id": "earbuds", "name": "earbuds", "one_in": 90, "rarity": 90, "odds": "90", "color": (48, 42, 109)},
    {"id": "envelope", "name": "envelope", "one_in": 91, "rarity": 91, "odds": "91", "color": (40, 196, 72)},
    {"id": "faucet", "name": "faucet", "one_in": 92, "rarity": 92, "odds": "92", "color": (98, 123, 51)},
    {"id": "flashlight", "name": "flashlight", "one_in": 94, "rarity": 94, "odds": "94", "color": (78, 203, 174)},
    {"id": "folder", "name": "folder", "one_in": 95, "rarity": 95, "odds": "95", "color": (70, 41, 43)},
    {"id": "fridge", "name": "fridge", "one_in": 98, "rarity": 98, "odds": "98", "color": (153, 140, 96)},
    {"id": "gloves", "name": "gloves", "one_in": 99, "rarity": 99, "odds": "99", "color": (216, 184, 76)},
    {"id": "hanger", "name": "hanger", "one_in": 103, "rarity": 103, "odds": "103", "color": (189, 73, 217)},
    {"id": "headphones", "name": "headphones", "one_in": 104, "rarity": 104, "odds": "104", "color": (41, 145, 89)},
    {"id": "helmet", "name": "helmet", "one_in": 107, "rarity": 107, "odds": "107", "color": (135, 106, 99)},
    {"id": "hose", "name": "hose", "one_in": 110, "rarity": 110, "odds": "110", "color": (57, 88, 98)},
    {"id": "jar", "name": "jar", "one_in": 114, "rarity": 114, "odds": "114", "color": (71, 57, 41)},
    {"id": "jeans", "name": "jeans", "one_in": 116, "rarity": 116, "odds": "116", "color": (91, 90, 223)},
    {"id": "keyboard", "name": "keyboard", "one_in": 119, "rarity": 119, "odds": "119", "color": (153, 57, 210)},
    {"id": "kite", "name": "kite", "one_in": 122, "rarity": 122, "odds": "122", "color": (181, 162, 100)},
    {"id": "knife", "name": "knife", "one_in": 126, "rarity": 126, "odds": "126", "color": (55, 131, 56)},
    {"id": "ladle", "name": "ladle", "one_in": 129, "rarity": 129, "odds": "129", "color": (76, 102, 67)},
    {"id": "laptop", "name": "laptop", "one_in": 134, "rarity": 134, "odds": "134", "color": (152, 61, 47)},
    {"id": "lemon", "name": "lemon", "one_in": 138, "rarity": 138, "odds": "138", "color": (67, 191, 69)},
    {"id": "lightbulb", "name": "lightbulb", "one_in": 140, "rarity": 140, "odds": "140", "color": (133, 49, 89)},
    {"id": "lipstick", "name": "lipstick", "one_in": 143, "rarity": 143, "odds": "143", "color": (107, 84, 52)},
    {"id": "lotion", "name": "lotion", "one_in": 147, "rarity": 147, "odds": "147", "color": (93, 85, 47)},
    {"id": "mailbox", "name": "mailbox", "one_in": 151, "rarity": 151, "odds": "151", "color": (212, 96, 161)},
    {"id": "matches", "name": "matches", "one_in": 155, "rarity": 155, "odds": "155", "color": (45, 151, 99)},
    {"id": "mattress", "name": "mattress", "one_in": 159, "rarity": 159, "odds": "159", "color": (155, 148, 76)},
    {"id": "microwave", "name": "microwave", "one_in": 164, "rarity": 164, "odds": "164", "color": (117, 185, 51)},
    {"id": "mop", "name": "mop", "one_in": 169, "rarity": 169, "odds": "169", "color": (148, 72, 41)},
    {"id": "nail", "name": "nail", "one_in": 174, "rarity": 174, "odds": "174", "color": (108, 102, 101)},
    {"id": "needle", "name": "needle", "one_in": 177, "rarity": 177, "odds": "177", "color": (53, 98, 94)},
    {"id": "oven", "name": "oven", "one_in": 183, "rarity": 183, "odds": "183", "color": (160, 75, 102)},
    {"id": "paintbrush", "name": "paintbrush", "one_in": 187, "rarity": 187, "odds": "187", "color": (168, 49, 57)},
    {"id": "pan", "name": "pan", "one_in": 192, "rarity": 192, "odds": "192", "color": (135, 83, 41)},
    {"id": "paperclip", "name": "paperclip", "one_in": 197, "rarity": 197, "odds": "197", "color": (40, 44, 229)},
    {"id": "peanut", "name": "peanut", "one_in": 203, "rarity": 203, "odds": "203", "color": (181, 173, 196)},
    {"id": "phone", "name": "phone", "one_in": 208, "rarity": 208, "odds": "208", "color": (194, 206, 77)},
    {"id": "pillowcase", "name": "pillowcase", "one_in": 214, "rarity": 214, "odds": "214", "color": (123, 103, 183)},
    {"id": "pitcher", "name": "pitcher", "one_in": 220, "rarity": 220, "odds": "220", "color": (119, 146, 61)},
    {"id": "pliers", "name": "pliers", "one_in": 226, "rarity": 226, "odds": "226", "color": (151, 149, 71)},
    {"id": "plug", "name": "plug", "one_in": 232, "rarity": 232, "odds": "232", "color": (128, 109, 103)},
    {"id": "popcorn", "name": "popcorn", "one_in": 238, "rarity": 238, "odds": "238", "color": (169, 67, 178)},
    {"id": "postcard", "name": "postcard", "one_in": 244, "rarity": 244, "odds": "244", "color": (72, 52, 99)},
    {"id": "pot", "name": "pot", "one_in": 251, "rarity": 251, "odds": "251", "color": (91, 85, 41)},
    {"id": "purse", "name": "purse", "one_in": 258, "rarity": 258, "odds": "258", "color": (89, 62, 84)},
    {"id": "radio", "name": "radio", "one_in": 265, "rarity": 265, "odds": "265", "color": (183, 59, 109)},
    {"id": "raincoat", "name": "raincoat", "one_in": 272, "rarity": 272, "odds": "272", "color": (153, 89, 54)},
    {"id": "rake", "name": "rake", "one_in": 279, "rarity": 279, "odds": "279", "color": (43, 86, 104)},
    {"id": "remote", "name": "remote", "one_in": 287, "rarity": 287, "odds": "287", "color": (148, 151, 117)},
    {"id": "rope", "name": "rope", "one_in": 295, "rarity": 295, "odds": "295", "color": (94, 146, 104)},
    {"id": "rug", "name": "rug", "one_in": 303, "rarity": 303, "odds": "303", "color": (150, 94, 41)},
    {"id": "sandals", "name": "sandals", "one_in": 311, "rarity": 311, "odds": "311", "color": (46, 224, 212)},
    {"id": "saucepan", "name": "saucepan", "one_in": 319, "rarity": 319, "odds": "319", "color": (120, 103, 175)},
    {"id": "saw", "name": "saw", "one_in": 328, "rarity": 328, "odds": "328", "color": (83, 96, 41)},
    {"id": "screwdriver", "name": "screwdriver", "one_in": 337, "rarity": 337, "odds": "337", "color": (152, 160, 105)},
    {"id": "shampoo", "name": "shampoo", "one_in": 346, "rarity": 346, "odds": "346", "color": (159, 47, 66)},
    {"id": "shelf", "name": "shelf", "one_in": 355, "rarity": 355, "odds": "355", "color": (122, 47, 131)},
    {"id": "shovel", "name": "shovel", "one_in": 365, "rarity": 365, "odds": "365", "color": (89, 62, 68)},
    {"id": "skillet", "name": "skillet", "one_in": 375, "rarity": 375, "odds": "375", "color": (224, 140, 210)},
    {"id": "slippers", "name": "slippers", "one_in": 385, "rarity": 385, "odds": "385", "color": (90, 54, 99)},
    {"id": "spatula", "name": "spatula", "one_in": 395, "rarity": 395, "odds": "395", "color": (100, 95, 49)},
    {"id": "speaker", "name": "speaker", "one_in": 406, "rarity": 406, "odds": "406", "color": (147, 43, 45)},
    {"id": "suitcase", "name": "suitcase", "one_in": 417, "rarity": 417, "odds": "417", "color": (73, 71, 113)},
    {"id": "sunglasses", "name": "sunglasses", "one_in": 428, "rarity": 428, "odds": "428", "color": (208, 92, 200)},
    {"id": "sweater", "name": "sweater", "one_in": 440, "rarity": 440, "odds": "440", "color": (67, 44, 130)},
    {"id": "tape", "name": "tape", "one_in": 451, "rarity": 451, "odds": "451", "color": (146, 111, 105)},
    {"id": "teapot", "name": "teapot", "one_in": 464, "rarity": 464, "odds": "464", "color": (55, 87, 91)},
    {"id": "television", "name": "television", "one_in": 476, "rarity": 476, "odds": "476", "color": (170, 45, 119)},
    {"id": "thermometer", "name": "thermometer", "one_in": 489, "rarity": 489, "odds": "489", "color": (180, 42, 68)},
    {"id": "thermos", "name": "thermos", "one_in": 502, "rarity": 502, "odds": "502", "color": (138, 61, 136)},
    {"id": "thread", "name": "thread", "one_in": 516, "rarity": 516, "odds": "516", "color": (64, 195, 88)},
    {"id": "thumbtack", "name": "thumbtack", "one_in": 530, "rarity": 530, "odds": "530", "color": (45, 143, 90)},
    {"id": "ticket", "name": "ticket", "one_in": 544, "rarity": 544, "odds": "544", "color": (44, 188, 98)},
    {"id": "tie", "name": "tie", "one_in": 559, "rarity": 559, "odds": "559", "color": (138, 101, 41)},
    {"id": "toaster", "name": "toaster", "one_in": 574, "rarity": 574, "odds": "574", "color": (202, 160, 148)},
    {"id": "toilet", "name": "toilet", "one_in": 590, "rarity": 590, "odds": "590", "color": (185, 157, 210)},
    {"id": "tongs", "name": "tongs", "one_in": 606, "rarity": 606, "odds": "606", "color": (83, 68, 153)},
    {"id": "tray", "name": "tray", "one_in": 622, "rarity": 622, "odds": "622", "color": (74, 181, 105)},
    {"id": "umbrella", "name": "umbrella", "one_in": 639, "rarity": 639, "odds": "639", "color": (60, 70, 171)},
    {"id": "vacuum", "name": "vacuum", "one_in": 656, "rarity": 656, "odds": "656", "color": (59, 117, 124)},
    {"id": "vase", "name": "vase", "one_in": 674, "rarity": 674, "odds": "674", "color": (183, 136, 106)},
    {"id": "vest", "name": "vest", "one_in": 692, "rarity": 692, "odds": "692", "color": (202, 153, 106)},
    {"id": "wallet", "name": "wallet", "one_in": 711, "rarity": 711, "odds": "711", "color": (177, 101, 214)},
    {"id": "watch", "name": "watch", "one_in": 730, "rarity": 730, "odds": "730", "color": (127, 183, 200)},
    {"id": "whisk", "name": "whisk", "one_in": 750, "rarity": 750, "odds": "750", "color": (110, 97, 204)},
    {"id": "whistle", "name": "whistle", "one_in": 770, "rarity": 770, "odds": "770", "color": (136, 65, 191)},
    {"id": "wrench", "name": "wrench", "one_in": 791, "rarity": 791, "odds": "791", "color": (207, 55, 72)},
    {"id": "yogurt", "name": "yogurt", "one_in": 812, "rarity": 812, "odds": "812", "color": (84, 119, 123)},
    {"id": "zipper", "name": "zipper", "one_in": 834, "rarity": 834, "odds": "834", "color": (100, 229, 104)},
    {"id": "armchair", "name": "armchair", "one_in": 857, "rarity": 857, "odds": "857", "color": (207, 87, 71)},
    {"id": "avocado", "name": "avocado", "one_in": 880, "rarity": 880, "odds": "880", "color": (229, 122, 74)},
    {"id": "ball", "name": "ball", "one_in": 904, "rarity": 904, "odds": "904", "color": (67, 144, 95)},
    {"id": "bell", "name": "bell", "one_in": 928, "rarity": 928, "odds": "928", "color": (71, 161, 95)},
    {"id": "binder", "name": "binder", "one_in": 953, "rarity": 953, "odds": "953", "color": (60, 203, 107)},
    {"id": "binoculars", "name": "binoculars", "one_in": 979, "rarity": 979, "odds": "979", "color": (122, 174, 120)},
    {"id": "blouse", "name": "blouse", "one_in": 1005, "rarity": 1005, "odds": "1,005", "color": (50, 45, 162)},
    {"id": "boots", "name": "boots", "one_in": 1033, "rarity": 1033, "odds": "1,033", "color": (47, 79, 84)},
    {"id": "bow", "name": "bow", "one_in": 1060, "rarity": 1060, "odds": "1,060", "color": (208, 215, 41)},
    {"id": "box", "name": "box", "one_in": 1089, "rarity": 1089, "odds": "1,089", "color": (209, 215, 41)},
    {"id": "bracelet", "name": "bracelet", "one_in": 1119, "rarity": 1119, "odds": "1,119", "color": (74, 206, 71)},
    {"id": "brownie", "name": "brownie", "one_in": 1149, "rarity": 1149, "odds": "1,149", "color": (158, 68, 61)},
    {"id": "bubble", "name": "bubble", "one_in": 1180, "rarity": 1180, "odds": "1,180", "color": (86, 84, 62)},
    {"id": "cabbage", "name": "cabbage", "one_in": 1212, "rarity": 1212, "odds": "1,212", "color": (157, 212, 86)},
    {"id": "cake", "name": "cake", "one_in": 1245, "rarity": 1245, "odds": "1,245", "color": (124, 94, 95)},
    {"id": "candy", "name": "candy", "one_in": 1278, "rarity": 1278, "odds": "1,278", "color": (89, 179, 94)},
    {"id": "cap", "name": "cap", "one_in": 1313, "rarity": 1313, "odds": "1,313", "color": (60, 218, 41)},
    {"id": "car", "name": "car", "one_in": 1348, "rarity": 1348, "odds": "1,348", "color": (62, 218, 41)},
    {"id": "carrot", "name": "carrot", "one_in": 1385, "rarity": 1385, "odds": "1,385", "color": (51, 158, 50)},
    {"id": "carton", "name": "carton", "one_in": 1422, "rarity": 1422, "odds": "1,422", "color": (175, 166, 50)},
    {"id": "celery", "name": "celery", "one_in": 1461, "rarity": 1461, "odds": "1,461", "color": (78, 126, 119)},
    {"id": "chip", "name": "chip", "one_in": 1501, "rarity": 1501, "odds": "1,501", "color": (78, 57, 96)},
    {"id": "chocolate", "name": "chocolate", "one_in": 1541, "rarity": 1541, "odds": "1,541", "color": (186, 43, 138)},
    {"id": "coat", "name": "coat", "one_in": 1582, "rarity": 1582, "odds": "1,582", "color": (207, 86, 96)},
    {"id": "cooler", "name": "cooler", "one_in": 1625, "rarity": 1625, "odds": "1,625", "color": (76, 53, 46)},
    {"id": "corn", "name": "corn", "one_in": 1669, "rarity": 1669, "odds": "1,669", "color": (60, 88, 96)},
    {"id": "cracker", "name": "cracker", "one_in": 1714, "rarity": 1714, "odds": "1,714", "color": (131, 103, 46)},
    {"id": "crate", "name": "crate", "one_in": 1761, "rarity": 1761, "odds": "1,761", "color": (55, 209, 103)},
    {"id": "crib", "name": "crib", "one_in": 1808, "rarity": 1808, "odds": "1,808", "color": (136, 100, 96)},
    {"id": "cucumber", "name": "cucumber", "one_in": 1857, "rarity": 1857, "odds": "1,857", "color": (62, 156, 108)},
    {"id": "curtain", "name": "curtain", "one_in": 1907, "rarity": 1907, "odds": "1,907", "color": (94, 104, 41)},
    {"id": "cushion", "name": "cushion", "one_in": 1959, "rarity": 1959, "odds": "1,959", "color": (99, 80, 52)},
    {"id": "desk", "name": "desk", "one_in": 2012, "rarity": 2012, "odds": "2,012", "color": (49, 186, 96)},
    {"id": "detergent", "name": "detergent", "one_in": 2066, "rarity": 2066, "odds": "2,066", "color": (76, 58, 68)},
    {"id": "dice", "name": "dice", "one_in": 2122, "rarity": 2122, "odds": "2,122", "color": (221, 201, 96)},
    {"id": "dish", "name": "dish", "one_in": 2180, "rarity": 2180, "odds": "2,180", "color": (50, 203, 96)},
    {"id": "doll", "name": "doll", "one_in": 2239, "rarity": 2239, "odds": "2,239", "color": (147, 228, 96)},
    {"id": "donut", "name": "donut", "one_in": 2299, "rarity": 2299, "odds": "2,299", "color": (84, 123, 120)},
    {"id": "drawer", "name": "drawer", "one_in": 2361, "rarity": 2361, "odds": "2,361", "color": (47, 40, 178)},
    {"id": "dress", "name": "dress", "one_in": 2425, "rarity": 2425, "odds": "2,425", "color": (169, 60, 121)},
    {"id": "drill", "name": "drill", "one_in": 2491, "rarity": 2491, "odds": "2,491", "color": (191, 76, 121)},
    {"id": "drum", "name": "drum", "one_in": 2558, "rarity": 2558, "odds": "2,558", "color": (128, 52, 96)},
    {"id": "dryer", "name": "dryer", "one_in": 2627, "rarity": 2627, "odds": "2,627", "color": (48, 77, 122)},
    {"id": "earring", "name": "earring", "one_in": 2698, "rarity": 2698, "odds": "2,698", "color": (48, 191, 117)},
    {"id": "fan", "name": "fan", "one_in": 2771, "rarity": 2771, "odds": "2,771", "color": (63, 40, 41)},
    {"id": "fence", "name": "fence", "one_in": 2846, "rarity": 2846, "odds": "2,846", "color": (43, 46, 151)},
    {"id": "fig", "name": "fig", "one_in": 2923, "rarity": 2923, "odds": "2,923", "color": (64, 41, 41)},
    {"id": "file", "name": "file", "one_in": 3002, "rarity": 3002, "odds": "3,002", "color": (200, 227, 97)},
    {"id": "fish", "name": "fish", "one_in": 3084, "rarity": 3084, "odds": "3,084", "color": (178, 228, 97)},
    {"id": "flag", "name": "flag", "one_in": 3167, "rarity": 3167, "odds": "3,167", "color": (100, 48, 97)},
    {"id": "flask", "name": "flask", "one_in": 3253, "rarity": 3253, "odds": "3,253", "color": (89, 208, 154)},
    {"id": "flower", "name": "flower", "one_in": 3340, "rarity": 3340, "odds": "3,340", "color": (119, 148, 57)},
    {"id": "frame", "name": "frame", "one_in": 3431, "rarity": 3431, "odds": "3,431", "color": (211, 91, 157)},
    {"id": "freezer", "name": "freezer", "one_in": 3524, "rarity": 3524, "odds": "3,524", "color": (91, 150, 103)},
    {"id": "garlic", "name": "garlic", "one_in": 3619, "rarity": 3619, "odds": "3,619", "color": (90, 104, 134)},
    {"id": "gate", "name": "gate", "one_in": 3717, "rarity": 3717, "odds": "3,717", "color": (41, 79, 98)},
    {"id": "glasses", "name": "glasses", "one_in": 3817, "rarity": 3817, "odds": "3,817", "color": (218, 78, 223)},
    {"id": "grape", "name": "grape", "one_in": 3921, "rarity": 3921, "odds": "3,921", "color": (183, 50, 176)},
    {"id": "grater", "name": "grater", "one_in": 4027, "rarity": 4027, "odds": "4,027", "color": (79, 149, 177)},
    {"id": "grill", "name": "grill", "one_in": 4135, "rarity": 4135, "odds": "4,135", "color": (66, 84, 176)},
    {"id": "guitar", "name": "guitar", "one_in": 4247, "rarity": 4247, "odds": "4,247", "color": (86, 65, 46)},
    {"id": "gum", "name": "gum", "one_in": 4362, "rarity": 4362, "odds": "4,362", "color": (209, 47, 41)},
    {"id": "hamper", "name": "hamper", "one_in": 4480, "rarity": 4480, "odds": "4,480", "color": (165, 161, 217)},
    {"id": "hat", "name": "hat", "one_in": 4601, "rarity": 4601, "odds": "4,601", "color": (133, 49, 41)},
    {"id": "highlighter", "name": "highlighter", "one_in": 4726, "rarity": 4726, "odds": "4,726", "color": (151, 109, 59)},
    {"id": "hoe", "name": "hoe", "one_in": 4853, "rarity": 4853, "odds": "4,853", "color": (68, 51, 41)},
    {"id": "hook", "name": "hook", "one_in": 4985, "rarity": 4985, "odds": "4,985", "color": (121, 88, 98)},
    {"id": "horn", "name": "horn", "one_in": 5120, "rarity": 5120, "odds": "5,120", "color": (223, 88, 98)},
    {"id": "jacket", "name": "jacket", "one_in": 5258, "rarity": 5258, "odds": "5,258", "color": (218, 97, 126)},
    {"id": "jam", "name": "jam", "one_in": 5400, "rarity": 5400, "odds": "5,400", "color": (66, 57, 41)},
    {"id": "jug", "name": "jug", "one_in": 5546, "rarity": 5546, "odds": "5,546", "color": (142, 60, 41)},
    {"id": "juicer", "name": "juicer", "one_in": 5696, "rarity": 5696, "odds": "5,696", "color": (42, 116, 45)},
    {"id": "ketchup", "name": "ketchup", "one_in": 5850, "rarity": 5850, "odds": "5,850", "color": (60, 194, 195)},
    {"id": "laundry", "name": "laundry", "one_in": 6008, "rarity": 6008, "odds": "6,008", "color": (199, 107, 129)},
    {"id": "lettuce", "name": "lettuce", "one_in": 6171, "rarity": 6171, "odds": "6,171", "color": (94, 134, 199)},
    {"id": "lid", "name": "lid", "one_in": 6338, "rarity": 6338, "odds": "6,338", "color": (129, 67, 41)},
    {"id": "lighter", "name": "lighter", "one_in": 6509, "rarity": 6509, "odds": "6,509", "color": (215, 81, 42)},
    {"id": "lock", "name": "lock", "one_in": 6685, "rarity": 6685, "odds": "6,685", "color": (113, 70, 101)},
    {"id": "lollipop", "name": "lollipop", "one_in": 6866, "rarity": 6866, "odds": "6,866", "color": (85, 71, 57)},
    {"id": "lunchbox", "name": "lunchbox", "one_in": 7052, "rarity": 7052, "odds": "7,052", "color": (107, 97, 95)},
    {"id": "magnet", "name": "magnet", "one_in": 7242, "rarity": 7242, "odds": "7,242", "color": (70, 91, 127)},
    {"id": "magnifier", "name": "magnifier", "one_in": 7438, "rarity": 7438, "odds": "7,438", "color": (90, 157, 67)},
    {"id": "mango", "name": "mango", "one_in": 7639, "rarity": 7639, "odds": "7,639", "color": (122, 169, 85)},
    {"id": "mask", "name": "mask", "one_in": 7846, "rarity": 7846, "odds": "7,846", "color": (84, 153, 101)},
    {"id": "mat", "name": "mat", "one_in": 8058, "rarity": 8058, "odds": "8,058", "color": (202, 70, 41)},
    {"id": "melon", "name": "melon", "one_in": 8276, "rarity": 8276, "odds": "8,276", "color": (131, 211, 87)},
    {"id": "mixer", "name": "mixer", "one_in": 8500, "rarity": 8500, "odds": "8,500", "color": (205, 54, 90)},
    {"id": "algorithm", "name": "algorithm", "one_in": 12001, "rarity": 12001, "odds": "12,001", "color": (111, 80, 60)},
    {"id": "alloy", "name": "alloy", "one_in": 12324, "rarity": 12324, "odds": "12,324", "color": (41, 132, 64)},
    {"id": "antibody", "name": "antibody", "one_in": 12656, "rarity": 12656, "odds": "12,656", "color": (226, 70, 217)},
    {"id": "aquifer", "name": "aquifer", "one_in": 12998, "rarity": 12998, "odds": "12,998", "color": (117, 162, 82)},
    {"id": "archipelago", "name": "archipelago", "one_in": 13349, "rarity": 13349, "odds": "13,349", "color": (73, 228, 98)},
    {"id": "atmosphere", "name": "atmosphere", "one_in": 13709, "rarity": 13709, "odds": "13,709", "color": (128, 84, 122)},
    {"id": "atom", "name": "atom", "one_in": 14079, "rarity": 14079, "odds": "14,079", "color": (91, 84, 95)},
    {"id": "axon", "name": "axon", "one_in": 14458, "rarity": 14458, "odds": "14,458", "color": (96, 101, 95)},
    {"id": "bacterium", "name": "bacterium", "one_in": 14849, "rarity": 14849, "odds": "14,849", "color": (164, 57, 124)},
    {"id": "barcode", "name": "barcode", "one_in": 15249, "rarity": 15249, "odds": "15,249", "color": (120, 41, 126)},
    {"id": "biome", "name": "biome", "one_in": 15661, "rarity": 15661, "odds": "15,661", "color": (54, 69, 80)},
    {"id": "biosphere", "name": "biosphere", "one_in": 16083, "rarity": 16083, "odds": "16,083", "color": (105, 207, 178)},
    {"id": "caldera", "name": "caldera", "one_in": 16517, "rarity": 16517, "odds": "16,517", "color": (212, 54, 78)},
    {"id": "capacitor", "name": "capacitor", "one_in": 16963, "rarity": 16963, "odds": "16,963", "color": (96, 135, 51)},
    {"id": "cartilage", "name": "cartilage", "one_in": 17421, "rarity": 17421, "odds": "17,421", "color": (212, 45, 41)},
    {"id": "catalyst", "name": "catalyst", "one_in": 17891, "rarity": 17891, "odds": "17,891", "color": (79, 124, 95)},
    {"id": "chromosome", "name": "chromosome", "one_in": 18373, "rarity": 18373, "odds": "18,373", "color": (228, 54, 59)},
    {"id": "circuit", "name": "circuit", "one_in": 18869, "rarity": 18869, "odds": "18,869", "color": (123, 131, 100)},
    {"id": "climate", "name": "climate", "one_in": 19378, "rarity": 19378, "odds": "19,378", "color": (41, 72, 132)},
    {"id": "conductor", "name": "conductor", "one_in": 19901, "rarity": 19901, "odds": "19,901", "color": (153, 155, 92)},
    {"id": "continent", "name": "continent", "one_in": 20438, "rarity": 20438, "odds": "20,438", "color": (218, 199, 153)},
    {"id": "cortex", "name": "cortex", "one_in": 20990, "rarity": 20990, "odds": "20,990", "color": (125, 62, 47)},
    {"id": "crater", "name": "crater", "one_in": 21556, "rarity": 21556, "odds": "21,556", "color": (137, 53, 92)},
    {"id": "dendrite", "name": "dendrite", "one_in": 22138, "rarity": 22138, "odds": "22,138", "color": (57, 160, 130)},
    {"id": "earthquake", "name": "earthquake", "one_in": 22735, "rarity": 22735, "odds": "22,735", "color": (179, 180, 71)},
    {"id": "ecosystem", "name": "ecosystem", "one_in": 23348, "rarity": 23348, "odds": "23,348", "color": (70, 71, 70)},
    {"id": "electrode", "name": "electrode", "one_in": 23978, "rarity": 23978, "odds": "23,978", "color": (65, 189, 100)},
    {"id": "electron", "name": "electron", "one_in": 24625, "rarity": 24625, "odds": "24,625", "color": (100, 215, 140)},
    {"id": "enzyme", "name": "enzyme", "one_in": 25290, "rarity": 25290, "odds": "25,290", "color": (128, 174, 204)},
    {"id": "equator", "name": "equator", "one_in": 25972, "rarity": 25972, "odds": "25,972", "color": (73, 111, 55)},
    {"id": "erosion", "name": "erosion", "one_in": 26673, "rarity": 26673, "odds": "26,673", "color": (41, 180, 41)},
    {"id": "estuary", "name": "estuary", "one_in": 27393, "rarity": 27393, "odds": "27,393", "color": (53, 79, 152)},
    {"id": "fungus", "name": "fungus", "one_in": 28132, "rarity": 28132, "odds": "28,132", "color": (160, 162, 153)},
    {"id": "genome", "name": "genome", "one_in": 28891, "rarity": 28891, "odds": "28,891", "color": (101, 99, 205)},
    {"id": "gravity", "name": "gravity", "one_in": 29670, "rarity": 29670, "odds": "29,670", "color": (46, 125, 224)},
    {"id": "greenhouse", "name": "greenhouse", "one_in": 30471, "rarity": 30471, "odds": "30,471", "color": (93, 94, 181)},
    {"id": "gyroscope", "name": "gyroscope", "one_in": 31293, "rarity": 31293, "odds": "31,293", "color": (101, 93, 77)},
    {"id": "helix", "name": "helix", "one_in": 32137, "rarity": 32137, "odds": "32,137", "color": (66, 88, 187)},
    {"id": "hormone", "name": "hormone", "one_in": 33005, "rarity": 33005, "odds": "33,005", "color": (224, 75, 75)},
    {"id": "hurricane", "name": "hurricane", "one_in": 33895, "rarity": 33895, "odds": "33,895", "color": (169, 130, 203)},
    {"id": "hydraulic", "name": "hydraulic", "one_in": 34810, "rarity": 34810, "odds": "34,810", "color": (141, 204, 156)},
    {"id": "hypothesis", "name": "hypothesis", "one_in": 35749, "rarity": 35749, "odds": "35,749", "color": (58, 183, 187)},
    {"id": "isotope", "name": "isotope", "one_in": 36713, "rarity": 36713, "odds": "36,713", "color": (139, 118, 104)},
    {"id": "lagoon", "name": "lagoon", "one_in": 37704, "rarity": 37704, "odds": "37,704", "color": (42, 56, 42)},
    {"id": "laser", "name": "laser", "one_in": 38721, "rarity": 38721, "odds": "38,721", "color": (65, 165, 67)},
    {"id": "latitude", "name": "latitude", "one_in": 39766, "rarity": 39766, "odds": "39,766", "color": (70, 78, 68)},
    {"id": "lichen", "name": "lichen", "one_in": 40839, "rarity": 40839, "odds": "40,839", "color": (91, 106, 185)},
    {"id": "limestone", "name": "limestone", "one_in": 41941, "rarity": 41941, "odds": "41,941", "color": (56, 143, 47)},
    {"id": "magnetosphere", "name": "magnetosphere", "one_in": 43073, "rarity": 43073, "odds": "43,073", "color": (92, 64, 128)},
    {"id": "mantle", "name": "mantle", "one_in": 44235, "rarity": 44235, "odds": "44,235", "color": (75, 76, 131)},
    {"id": "membrane", "name": "membrane", "one_in": 45429, "rarity": 45429, "odds": "45,429", "color": (111, 160, 89)},
    {"id": "mineral", "name": "mineral", "one_in": 46654, "rarity": 46654, "odds": "46,654", "color": (50, 139, 161)},
    {"id": "molecule", "name": "molecule", "one_in": 47913, "rarity": 47913, "odds": "47,913", "color": (64, 59, 59)},
    {"id": "monsoon", "name": "monsoon", "one_in": 49206, "rarity": 49206, "odds": "49,206", "color": (83, 99, 167)},
    {"id": "neuron", "name": "neuron", "one_in": 50534, "rarity": 50534, "odds": "50,534", "color": (63, 100, 103)},
    {"id": "neutron", "name": "neutron", "one_in": 51897, "rarity": 51897, "odds": "51,897", "color": (51, 79, 205)},
    {"id": "nucleus", "name": "nucleus", "one_in": 53298, "rarity": 53298, "odds": "53,298", "color": (167, 68, 214)},
    {"id": "ore", "name": "ore", "one_in": 54736, "rarity": 54736, "odds": "54,736", "color": (110, 81, 41)},
    {"id": "organelle", "name": "organelle", "one_in": 56213, "rarity": 56213, "odds": "56,213", "color": (225, 141, 96)},
    {"id": "oxygen", "name": "oxygen", "one_in": 57729, "rarity": 57729, "odds": "57,729", "color": (226, 95, 212)},
    {"id": "ozone", "name": "ozone", "one_in": 59287, "rarity": 59287, "odds": "59,287", "color": (85, 148, 69)},
    {"id": "pendulum", "name": "pendulum", "one_in": 60887, "rarity": 60887, "odds": "60,887", "color": (146, 77, 154)},
    {"id": "photon", "name": "photon", "one_in": 62530, "rarity": 62530, "odds": "62,530", "color": (64, 189, 68)},
    {"id": "plasma", "name": "plasma", "one_in": 64217, "rarity": 64217, "odds": "64,217", "color": (102, 109, 67)},
    {"id": "polymer", "name": "polymer", "one_in": 65949, "rarity": 65949, "odds": "65,949", "color": (208, 41, 117)},
    {"id": "protein", "name": "protein", "one_in": 67729, "rarity": 67729, "odds": "67,729", "color": (201, 203, 168)},
    {"id": "radar", "name": "radar", "one_in": 69556, "rarity": 69556, "odds": "69,556", "color": (178, 58, 109)},
    {"id": "radiation", "name": "radiation", "one_in": 71433, "rarity": 71433, "odds": "71,433", "color": (131, 59, 78)},
    {"id": "reactor", "name": "reactor", "one_in": 73361, "rarity": 73361, "odds": "73,361", "color": (56, 204, 67)},
    {"id": "resin", "name": "resin", "one_in": 75340, "rarity": 75340, "odds": "75,340", "color": (75, 106, 112)},
    {"id": "seismograph", "name": "seismograph", "one_in": 77373, "rarity": 77373, "odds": "77,373", "color": (106, 87, 150)},
    {"id": "skeleton", "name": "skeleton", "one_in": 79461, "rarity": 79461, "odds": "79,461", "color": (77, 44, 198)},
    {"id": "spore", "name": "spore", "one_in": 81605, "rarity": 81605, "odds": "81,605", "color": (209, 123, 136)},
    {"id": "stalactite", "name": "stalactite", "one_in": 83806, "rarity": 83806, "odds": "83,806", "color": (56, 99, 82)},
    {"id": "stratum", "name": "stratum", "one_in": 86068, "rarity": 86068, "odds": "86,068", "color": (58, 52, 109)},
    {"id": "synapse", "name": "synapse", "one_in": 88390, "rarity": 88390, "odds": "88,390", "color": (203, 74, 207)},
    {"id": "tectonic", "name": "tectonic", "one_in": 90775, "rarity": 90775, "odds": "90,775", "color": (225, 104, 88)},
    {"id": "tendon", "name": "tendon", "one_in": 93224, "rarity": 93224, "odds": "93,224", "color": (208, 69, 98)},
    {"id": "tornado", "name": "tornado", "one_in": 95740, "rarity": 95740, "odds": "95,740", "color": (127, 50, 197)},
    {"id": "transistor", "name": "transistor", "one_in": 98323, "rarity": 98323, "odds": "98,323", "color": (193, 90, 194)},
    {"id": "trench", "name": "trench", "one_in": 100976, "rarity": 100976, "odds": "100,976", "color": (46, 189, 72)},
    {"id": "turbine", "name": "turbine", "one_in": 103701, "rarity": 103701, "odds": "103,701", "color": (67, 180, 189)},
    {"id": "ultrasound", "name": "ultrasound", "one_in": 106499, "rarity": 106499, "odds": "106,499", "color": (217, 51, 99)},
    {"id": "wavelength", "name": "wavelength", "one_in": 109372, "rarity": 109372, "odds": "109,372", "color": (189, 109, 153)},
    {"id": "wetland", "name": "wetland", "one_in": 112323, "rarity": 112323, "odds": "112,323", "color": (57, 107, 131)},
    {"id": "xray", "name": "xray", "one_in": 115354, "rarity": 115354, "odds": "115,354", "color": (140, 41, 107)},
    {"id": "zeolite", "name": "zeolite", "one_in": 118467, "rarity": 118467, "odds": "118,467", "color": (132, 202, 89)},
    {"id": "zircon", "name": "zircon", "one_in": 121663, "rarity": 121663, "odds": "121,663", "color": (221, 200, 105)},
    {"id": "abacus", "name": "abacus", "one_in": 124946, "rarity": 124946, "odds": "124,946", "color": (57, 211, 144)},
    {"id": "accumulator", "name": "accumulator", "one_in": 128317, "rarity": 128317, "odds": "128,317", "color": (42, 40, 229)},
    {"id": "acid", "name": "acid", "one_in": 131780, "rarity": 131780, "odds": "131,780", "color": (59, 77, 94)},
    {"id": "aerogel", "name": "aerogel", "one_in": 135335, "rarity": 135335, "odds": "135,335", "color": (41, 191, 223)},
    {"id": "algae", "name": "algae", "one_in": 138987, "rarity": 138987, "odds": "138,987", "color": (68, 108, 64)},
    {"id": "alkali", "name": "alkali", "one_in": 142737, "rarity": 142737, "odds": "142,737", "color": (88, 58, 75)},
    {"id": "alluvium", "name": "alluvium", "one_in": 146589, "rarity": 146589, "odds": "146,589", "color": (151, 76, 98)},
    {"id": "amino", "name": "amino", "one_in": 150544, "rarity": 150544, "odds": "150,544", "color": (156, 69, 64)},
    {"id": "amplifier", "name": "amplifier", "one_in": 154606, "rarity": 154606, "odds": "154,606", "color": (97, 95, 99)},
    {"id": "anemometer", "name": "anemometer", "one_in": 158777, "rarity": 158777, "odds": "158,777", "color": (55, 58, 66)},
    {"id": "antenna", "name": "antenna", "one_in": 163062, "rarity": 163062, "odds": "163,062", "color": (173, 67, 62)},
    {"id": "anticline", "name": "anticline", "one_in": 167461, "rarity": 167461, "odds": "167,461", "color": (191, 101, 103)},
    {"id": "antigen", "name": "antigen", "one_in": 171980, "rarity": 171980, "odds": "171,980", "color": (78, 86, 64)},
    {"id": "anvil", "name": "anvil", "one_in": 176620, "rarity": 176620, "odds": "176,620", "color": (162, 198, 65)},
    {"id": "aperture", "name": "aperture", "one_in": 181386, "rarity": 181386, "odds": "181,386", "color": (144, 53, 125)},
    {"id": "arch", "name": "arch", "one_in": 186280, "rarity": 186280, "odds": "186,280", "color": (72, 74, 95)},
    {"id": "armature", "name": "armature", "one_in": 191306, "rarity": 191306, "odds": "191,306", "color": (137, 83, 41)},
    {"id": "artery", "name": "artery", "one_in": 196468, "rarity": 196468, "odds": "196,468", "color": (95, 207, 188)},
    {"id": "atoll", "name": "atoll", "one_in": 201769, "rarity": 201769, "odds": "201,769", "color": (132, 53, 68)},
    {"id": "autoclave", "name": "autoclave", "one_in": 207214, "rarity": 207214, "odds": "207,214", "color": (172, 200, 51)},
    {"id": "avalanche", "name": "avalanche", "one_in": 212805, "rarity": 212805, "odds": "212,805", "color": (203, 143, 126)},
    {"id": "barometer", "name": "barometer", "one_in": 218547, "rarity": 218547, "odds": "218,547", "color": (169, 139, 72)},
    {"id": "bedrock", "name": "bedrock", "one_in": 224444, "rarity": 224444, "odds": "224,444", "color": (130, 108, 222)},
    {"id": "benthic", "name": "benthic", "one_in": 230500, "rarity": 230500, "odds": "230,500", "color": (69, 93, 148)},
    {"id": "binomial", "name": "binomial", "one_in": 236719, "rarity": 236719, "odds": "236,719", "color": (115, 55, 172)},
    {"id": "borehole", "name": "borehole", "one_in": 243106, "rarity": 243106, "odds": "243,106", "color": (120, 174, 104)},
    {"id": "boulder", "name": "boulder", "one_in": 249666, "rarity": 249666, "odds": "249,666", "color": (149, 42, 98)},
    {"id": "brachiopod", "name": "brachiopod", "one_in": 256402, "rarity": 256402, "odds": "256,402", "color": (163, 136, 152)},
    {"id": "brine", "name": "brine", "one_in": 263321, "rarity": 263321, "odds": "263,321", "color": (58, 217, 85)},
    {"id": "calcite", "name": "calcite", "one_in": 270426, "rarity": 270426, "odds": "270,426", "color": (189, 121, 78)},
    {"id": "calcium", "name": "calcium", "one_in": 277723, "rarity": 277723, "odds": "277,723", "color": (40, 121, 78)},
    {"id": "capillary", "name": "capillary", "one_in": 285216, "rarity": 285216, "odds": "285,216", "color": (105, 64, 128)},
    {"id": "carbohydrate", "name": "carbohydrate", "one_in": 292912, "rarity": 292912, "odds": "292,912", "color": (66, 198, 131)},
    {"id": "carcinogen", "name": "carcinogen", "one_in": 300815, "rarity": 300815, "odds": "300,815", "color": (65, 55, 110)},
    {"id": "cascade", "name": "cascade", "one_in": 308932, "rarity": 308932, "odds": "308,932", "color": (44, 67, 138)},
    {"id": "cathode", "name": "cathode", "one_in": 317268, "rarity": 317268, "odds": "317,268", "color": (98, 84, 159)},
    {"id": "cave", "name": "cave", "one_in": 325828, "rarity": 325828, "odds": "325,828", "color": (41, 95, 95)},
    {"id": "cellulose", "name": "cellulose", "one_in": 334620, "rarity": 334620, "odds": "334,620", "color": (50, 50, 65)},
    {"id": "cement", "name": "cement", "one_in": 343649, "rarity": 343649, "odds": "343,649", "color": (228, 76, 119)},
    {"id": "centrifuge", "name": "centrifuge", "one_in": 352921, "rarity": 352921, "odds": "352,921", "color": (86, 49, 149)},
    {"id": "ceramic", "name": "ceramic", "one_in": 362444, "rarity": 362444, "odds": "362,444", "color": (94, 165, 204)},
    {"id": "chert", "name": "chert", "one_in": 372223, "rarity": 372223, "odds": "372,223", "color": (62, 102, 98)},
    {"id": "chlorophyll", "name": "chlorophyll", "one_in": 382267, "rarity": 382267, "odds": "382,267", "color": (88, 172, 217)},
    {"id": "cinder cone", "name": "cinder cone", "one_in": 392581, "rarity": 392581, "odds": "392,581", "color": (98, 205, 168)},
    {"id": "cirrus", "name": "cirrus", "one_in": 403174, "rarity": 403174, "odds": "403,174", "color": (66, 98, 195)},
    {"id": "cleavage", "name": "cleavage", "one_in": 414053, "rarity": 414053, "odds": "414,053", "color": (66, 203, 229)},
    {"id": "cloud chamber", "name": "cloud chamber", "one_in": 425225, "rarity": 425225, "odds": "425,225", "color": (81, 162, 42)},
    {"id": "cobalt", "name": "cobalt", "one_in": 436698, "rarity": 436698, "odds": "436,698", "color": (125, 40, 104)},
    {"id": "cochlea", "name": "cochlea", "one_in": 448481, "rarity": 448481, "odds": "448,481", "color": (183, 158, 86)},
    {"id": "compressor", "name": "compressor", "one_in": 460582, "rarity": 460582, "odds": "460,582", "color": (181, 73, 72)},
    {"id": "condenser", "name": "condenser", "one_in": 473010, "rarity": 473010, "odds": "473,010", "color": (41, 88, 64)},
    {"id": "conifer", "name": "conifer", "one_in": 485773, "rarity": 485773, "odds": "485,773", "color": (46, 97, 219)},
    {"id": "convection", "name": "convection", "one_in": 498880, "rarity": 498880, "odds": "498,880", "color": (192, 171, 174)},
    {"id": "core sample", "name": "core sample", "one_in": 512341, "rarity": 512341, "odds": "512,341", "color": (51, 78, 156)},
    {"id": "crevasse", "name": "crevasse", "one_in": 526165, "rarity": 526165, "odds": "526,165", "color": (68, 71, 51)},
    {"id": "crust", "name": "crust", "one_in": 540363, "rarity": 540363, "odds": "540,363", "color": (57, 104, 103)},
    {"id": "cytoplasm", "name": "cytoplasm", "one_in": 554943, "rarity": 554943, "odds": "554,943", "color": (100, 60, 221)},
    {"id": "debris", "name": "debris", "one_in": 569916, "rarity": 569916, "odds": "569,916", "color": (67, 97, 199)},
    {"id": "densitometer", "name": "densitometer", "one_in": 585294, "rarity": 585294, "odds": "585,294", "color": (61, 133, 123)},
    {"id": "deposition", "name": "deposition", "one_in": 601087, "rarity": 601087, "odds": "601,087", "color": (104, 158, 157)},
    {"id": "detector", "name": "detector", "one_in": 617305, "rarity": 617305, "odds": "617,305", "color": (194, 161, 139)},
    {"id": "diatom", "name": "diatom", "one_in": 633962, "rarity": 633962, "odds": "633,962", "color": (40, 64, 81)},
    {"id": "dike", "name": "dike", "one_in": 651067, "rarity": 651067, "odds": "651,067", "color": (229, 202, 96)},
    {"id": "diode", "name": "diode", "one_in": 668635, "rarity": 668635, "odds": "668,635", "color": (205, 51, 117)},
    {"id": "dipole", "name": "dipole", "one_in": 686676, "rarity": 686676, "odds": "686,676", "color": (229, 100, 89)},
    {"id": "discharge", "name": "discharge", "one_in": 705204, "rarity": 705204, "odds": "705,204", "color": (146, 181, 173)},
    {"id": "dislocation", "name": "dislocation", "one_in": 724232, "rarity": 724232, "odds": "724,232", "color": (161, 206, 46)},
    {"id": "distillate", "name": "distillate", "one_in": 743774, "rarity": 743774, "odds": "743,774", "color": (87, 64, 88)},
    {"id": "doldrums", "name": "doldrums", "one_in": 763842, "rarity": 763842, "odds": "763,842", "color": (114, 225, 158)},
    {"id": "dolomite", "name": "dolomite", "one_in": 784453, "rarity": 784453, "odds": "784,453", "color": (229, 64, 98)},
    {"id": "drainage", "name": "drainage", "one_in": 805619, "rarity": 805619, "odds": "805,619", "color": (227, 203, 60)},
    {"id": "drift", "name": "drift", "one_in": 827356, "rarity": 827356, "odds": "827,356", "color": (67, 75, 121)},
    {"id": "drought", "name": "drought", "one_in": 849680, "rarity": 849680, "odds": "849,680", "color": (133, 135, 48)},
    {"id": "drumlin", "name": "drumlin", "one_in": 872607, "rarity": 872607, "odds": "872,607", "color": (227, 204, 86)},
    {"id": "dune", "name": "dune", "one_in": 896152, "rarity": 896152, "odds": "896,152", "color": (84, 64, 96)},
    {"id": "dynamo", "name": "dynamo", "one_in": 920332, "rarity": 920332, "odds": "920,332", "color": (208, 152, 55)},
    {"id": "eddy", "name": "eddy", "one_in": 945165, "rarity": 945165, "odds": "945,165", "color": (46, 65, 97)},
    {"id": "effluent", "name": "effluent", "one_in": 970667, "rarity": 970667, "odds": "970,667", "color": (67, 196, 167)},
    {"id": "electrolysis", "name": "electrolysis", "one_in": 996858, "rarity": 996858, "odds": "996,858", "color": (106, 53, 170)},
    {"id": "embryo", "name": "embryo", "one_in": 1023756, "rarity": 1023756, "odds": "1,023,756", "color": (182, 80, 173)},
    {"id": "endemic", "name": "endemic", "one_in": 1051379, "rarity": 1051379, "odds": "1,051,379", "color": (189, 103, 196)},
    {"id": "epicenter", "name": "epicenter", "one_in": 1079748, "rarity": 1079748, "odds": "1,079,748", "color": (41, 120, 67)},
    {"id": "esker", "name": "esker", "one_in": 1108882, "rarity": 1108882, "odds": "1,108,882", "color": (66, 183, 140)},
    {"id": "eutrophication", "name": "eutrophication", "one_in": 1138802, "rarity": 1138802, "odds": "1,138,802", "color": (86, 112, 50)},
    {"id": "evaporation", "name": "evaporation", "one_in": 1169530, "rarity": 1169530, "odds": "1,169,530", "color": (112, 165, 89)},
    {"id": "exoskeleton", "name": "exoskeleton", "one_in": 1201086, "rarity": 1201086, "odds": "1,201,086", "color": (217, 115, 67)},
    {"id": "fault", "name": "fault", "one_in": 1233494, "rarity": 1233494, "odds": "1,233,494", "color": (100, 94, 148)},
    {"id": "feldspar", "name": "feldspar", "one_in": 1266777, "rarity": 1266777, "odds": "1,266,777", "color": (57, 161, 92)},
    {"id": "fermentation", "name": "fermentation", "one_in": 1300957, "rarity": 1300957, "odds": "1,300,957", "color": (116, 208, 149)},
    {"id": "filament", "name": "filament", "one_in": 1336060, "rarity": 1336060, "odds": "1,336,060", "color": (88, 211, 77)},
    {"id": "firn", "name": "firn", "one_in": 1372110, "rarity": 1372110, "odds": "1,372,110", "color": (151, 228, 97)},
    {"id": "floodplain", "name": "floodplain", "one_in": 1409133, "rarity": 1409133, "odds": "1,409,133", "color": (208, 199, 84)},
    {"id": "flora", "name": "flora", "one_in": 1447155, "rarity": 1447155, "odds": "1,447,155", "color": (188, 77, 154)},
    {"id": "fluorescence", "name": "fluorescence", "one_in": 1486202, "rarity": 1486202, "odds": "1,486,202", "color": (166, 43, 137)},
    {"id": "fog", "name": "fog", "one_in": 1526303, "rarity": 1526303, "odds": "1,526,303", "color": (196, 42, 41)},
    {"id": "foraminifera", "name": "foraminifera", "one_in": 1567486, "rarity": 1567486, "odds": "1,567,486", "color": (123, 100, 86)},
    {"id": "fracture", "name": "fracture", "one_in": 1609781, "rarity": 1609781, "odds": "1,609,781", "color": (100, 131, 87)},
    {"id": "frequency", "name": "frequency", "one_in": 1653217, "rarity": 1653217, "odds": "1,653,217", "color": (90, 88, 221)},
    {"id": "frost line", "name": "frost line", "one_in": 1697824, "rarity": 1697824, "odds": "1,697,824", "color": (62, 101, 211)},
    {"id": "fulcrum", "name": "fulcrum", "one_in": 1743635, "rarity": 1743635, "odds": "1,743,635", "color": (72, 130, 162)},
    {"id": "fusion", "name": "fusion", "one_in": 1790683, "rarity": 1790683, "odds": "1,790,683", "color": (60, 104, 156)},
    {"id": "galvanometer", "name": "galvanometer", "one_in": 1838999, "rarity": 1838999, "odds": "1,838,999", "color": (77, 40, 86)},
    {"id": "generator", "name": "generator", "one_in": 1888620, "rarity": 1888620, "odds": "1,888,620", "color": (47, 213, 151)},
    {"id": "gene", "name": "gene", "one_in": 1939579, "rarity": 1939579, "odds": "1,939,579", "color": (103, 95, 98)},
    {"id": "geode crystal", "name": "geode crystal", "one_in": 1991914, "rarity": 1991914, "odds": "1,991,914", "color": (46, 129, 143)},
    {"id": "geyser vent", "name": "geyser vent", "one_in": 2045660, "rarity": 2045660, "odds": "2,045,660", "color": (212, 52, 47)},
    {"id": "ginkgo", "name": "ginkgo", "one_in": 2100857, "rarity": 2100857, "odds": "2,100,857", "color": (103, 180, 87)},
    {"id": "gneiss", "name": "gneiss", "one_in": 2157543, "rarity": 2157543, "odds": "2,157,543", "color": (145, 56, 107)},
    {"id": "graphite", "name": "graphite", "one_in": 2215758, "rarity": 2215758, "odds": "2,215,758", "color": (124, 207, 125)},
    {"id": "groundwater", "name": "groundwater", "one_in": 2275544, "rarity": 2275544, "odds": "2,275,544", "color": (186, 137, 159)},
    {"id": "gypsum", "name": "gypsum", "one_in": 2336944, "rarity": 2336944, "odds": "2,336,944", "color": (79, 120, 56)},
    {"id": "habitat", "name": "habitat", "one_in": 2400001, "rarity": 2400001, "odds": "2,400,001", "color": (103, 42, 62)},
    {"id": "buff", "name": "buff", "one_in": 1000, "rarity": 1000, "odds": "1,000", "color": (139, 228, 95)},
    {"id": "super buff", "name": "super buff", "one_in": 10000, "rarity": 10000, "odds": "10,000", "color": (58, 64, 180)},
)
for rarity in RARITIES:
    number = rarity.get("rarity", 1 + (rarity["one_in"] - 2) * 4)
    rarity["rarity"] = number
    rarity["odds"] = f"{number:,}"
RARITIES = tuple(sorted(RARITIES, key=lambda item: item["rarity"], reverse=True))
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
pointer_x = -1.0
pointer_y = -1.0
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
clover_tier = 0
buff_count = 0
super_buff_count = 0
autoclicker_owned = False
autoclicker_on = False
roll_pad = 0.06
roll_over = 0.26
roll_back = 0.42
roll_ready = 0.0
next_multi = 1
NEXT_MULTI = {"lucky": 2, "super lucky": 3, "ultra lucky": 5}
STRIP_TILE = 188
payout_shown = 0
payout_until = 0.0
shop_open = False
board_open = False
board_scroll = 0
board_rows: list[dict] = []
board_note = ""
username = ""
player_id = ""
best_id = ""
best_rarity = 0
reset_taps = 0
POTION_COST = 375
SPEED_COST = 450
MEGA_COST = 12000
CLOVER_COST = (1000, 2500, 10000, 100000, 250000, 500000, 1000000)
CLOVER_LUCK = (1.0, 1.10, 1.25, 1.50, 1.80, 1.90, 2.00, 2.50)
CLOVER_NAME = ("4 leaf clover", "5 leaf clover", "6 leaf clover", "7 leaf clover", "8 leaf clover", "9 leaf clover", "10 leaf clover")
CLOVER_NOTE = ("10% increase", "25% increase", "50% increase", "80% increase", "90% increase", "100% increase", "150% increase")
AUTO_COST = 3000
POTION_SECONDS = 300
ROLL_BOX = (GAME_W // 2 - 74, 196, 148, 34)
DEX_BOX = (GAME_W // 2 - 74, 242, 148, 30)
SHOP_BOX = (GAME_W // 2 - 74, 284, 148, 30)
BOARD_BOX = (GAME_W // 2 - 74, 326, 148, 30)
NAME_BOX = (12, 44, 150, 24)
RESET_BOX = (12, GAME_H - 34, 64, 22)
BUY_LUCK_BOX = (GAME_W // 2 - 220, 148, 140, 28)
BUY_SPEED_BOX = (GAME_W // 2 + 80, 148, 140, 28)
BUY_MEGA_BOX = (GAME_W // 2 - 220, 244, 140, 28)
BUY_CLOVER_BOX = (GAME_W // 2 + 80, 244, 140, 28)
BUY_AUTO_BOX = (GAME_W // 2 - 70, 324, 140, 28)
BACK_BOX = (GAME_W // 2 - 52, 368, 104, 28)


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
        for folder in (AUDIO_DIR, DOWNLOADS):
            hit = None
            for name in (f"song{number}.mp3", f"song {number}.mp3", f"Song {number}.mp3"):
                path = folder / name
                if path.exists():
                    hit = path
                    break
            if hit is not None:
                found.append(hit)
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
    stem = "".join(ch if ch.isalnum() else "_" for ch in path.stem)
    dest = CACHE / f"{stem}.mp3"
    quiet = CACHE / f"{stem}_q40.mp3"
    if FFMPEG:
        fresh = quiet.exists() and quiet.stat().st_size > 1000 and quiet.stat().st_mtime >= path.stat().st_mtime
        if not fresh:
            subprocess.run(
                [FFMPEG, "-y", "-v", "error", "-i", str(path), "-filter:a", "volume=0.4", "-c:a", "libmp3lame", "-q:a", "4", str(quiet)],
                capture_output=True,
            )
        if quiet.exists() and quiet.stat().st_size > 1000:
            return quiet
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


WHEEL = tuple(1 / rarity["rarity"] for rarity in RARITIES)
WHEEL_TOTAL = sum(WHEEL)
for rarity in RARITIES:
    rarity["chance"] = f"1 in {max(1, round(WHEEL_TOTAL * rarity['rarity'])):,}"


def spin_wheel() -> dict:
    mark = random.random() * WHEEL_TOTAL
    for rarity, weight in zip(RARITIES, WHEEL):
        mark -= weight
        if mark <= 0:
            return rarity
    return RARITIES[-1]


def luck_spins(boost: float) -> int:
    clover = CLOVER_LUCK[min(len(CLOVER_LUCK) - 1, max(0, clover_tier))]
    scaled = (float(boost) + buff_count) * clover * (1 + 0.05 * super_buff_count)
    spins = int(scaled)
    if random.random() < scaled - spins:
        spins += 1
    return max(1, spins)


def gambler_pace() -> float:
    if roll_count >= 10000:
        return 1.80
    if roll_count >= 4000:
        return 1.70
    if roll_count >= 2000:
        return 1.60
    if roll_count >= 1600:
        return 1.55
    if roll_count >= 800:
        return 1.50
    if roll_count >= 400:
        return 1.40
    if roll_count >= 200:
        return 1.30
    if roll_count >= 100:
        return 1.20
    return 1.0


def gambler_name() -> str | None:
    if roll_count >= 10000:
        return "apex gambler +80%"
    if roll_count >= 4000:
        return "turbo gambler +70%"
    if roll_count >= 2000:
        return "hyper gambler +60%"
    if roll_count >= 1600:
        return "max gambler +55%"
    if roll_count >= 800:
        return "ultra gambler +50%"
    if roll_count >= 400:
        return "rapid fire +40%"
    if roll_count >= 200:
        return "spam clicker +30%"
    if roll_count >= 100:
        return "speedy gambler +20%"
    return None


def pick_rarity(boost: int | None = None) -> dict:
    if boost is None:
        boost = luck_now()
    best = spin_wheel()
    for _ in range(luck_spins(boost) - 1):
        rolled = spin_wheel()
        if rolled["rarity"] > best["rarity"]:
            best = rolled
    return best


def progress_body() -> dict:
    return {
        "autoclicker_on": autoclicker_on,
        "autoclicker_owned": autoclicker_owned,
        "best_id": best_id,
        "best_rarity": best_rarity,
        "buff_count": buff_count,
        "clover_tier": clover_tier,
        "found": found,
        "mega_left": mega_left,
        "money": money,
        "player_id": player_id,
        "potion_until": potion_until,
        "rolls": roll_count,
        "speed_until": speed_until,
        "super_buff_count": super_buff_count,
        "username": username,
    }


def seal_text(payload: str) -> str:
    mix = 2166136261
    for char in payload + "test-your-luck-seal-v1":
        mix ^= ord(char)
        mix = (mix * 16777619) & 0xFFFFFFFF
    return f"{mix:08x}"


def apply_progress(data: dict) -> None:
    global roll_count, found, money, potion_until, speed_until, mega_left, clover_tier, autoclicker_owned, autoclicker_on
    global username, player_id, best_id, best_rarity, buff_count, super_buff_count
    roll_count = max(0, int(data.get("rolls", 0)))
    money = max(0, int(data.get("money", 0)))
    potion_until = float(data.get("potion_until", 0))
    speed_until = float(data.get("speed_until", 0))
    mega_left = max(0, int(data.get("mega_left", 0)))
    clover_tier = min(len(CLOVER_NAME), max(0, int(data.get("clover_tier", 0))))
    autoclicker_owned = bool(data.get("autoclicker_owned", False))
    autoclicker_on = bool(data.get("autoclicker_on", False)) and autoclicker_owned
    loaded = data.get("found", {})
    found = loaded if isinstance(loaded, dict) else {}
    username = clean_name(str(data.get("username", "")))
    player_id = str(data.get("player_id", "") or "")
    best_id = str(data.get("best_id", "") or "")
    best_rarity = max(0, int(data.get("best_rarity", 0) or 0))
    buff_count = max(0, int(data.get("buff_count", 0) or 0))
    super_buff_count = max(0, int(data.get("super_buff_count", 0) or 0))
    sync_best_from_found()


def load_progress() -> None:
    if not SAVE.exists():
        return
    try:
        data = json.loads(SAVE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(data, dict):
        return
    if "body" in data:
        body = data.get("body")
        if not isinstance(body, str) or data.get("seal") != seal_text(body):
            return
        try:
            saved = json.loads(body)
        except json.JSONDecodeError:
            return
        if isinstance(saved, dict):
            apply_progress(saved)
        return
    if SAVE.with_name("bestiary.lock").exists():
        return
    apply_progress(data)
    store_progress()


def store_progress() -> None:
    body = json.dumps(progress_body(), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    SAVE.write_text(
        json.dumps({"body": body, "seal": seal_text(body)}),
        encoding="utf-8",
    )
    SAVE.with_name("bestiary.lock").write_text("1", encoding="utf-8")


BOARD_ROOT = "https://mantledb.sh/v2/tyl-luck-board-7f3a"


def clean_name(raw: str) -> str:
    return "".join(char for char in raw.strip() if char >= " " and char != "\x7f")[:16]


def known_item(item_id: str) -> dict | None:
    return next((row for row in RARITIES if row["id"] == item_id), None)


def sync_best_from_found() -> None:
    global best_id, best_rarity
    top = best_rarity
    top_id = best_id
    for item_id, slot in found.items():
        if int(slot.get("count", 0)) <= 0:
            continue
        item = known_item(str(item_id))
        if item is not None and int(item["rarity"]) > top:
            top = int(item["rarity"])
            top_id = item["id"]
    best_rarity = top
    best_id = top_id


def ensure_player() -> None:
    global player_id
    if not player_id:
        player_id = uuid.uuid4().hex


def push_best() -> None:
    if not player_id and not username and not best_id:
        return
    created = not player_id
    ensure_player()
    if created:
        store_progress()
    payload = json.dumps({"name": username, "id": best_id}).encode("utf-8")
    target = f"{BOARD_ROOT}/p/{player_id}"

    def send() -> None:
        try:
            request = urllib.request.Request(
                target,
                data=payload,
                method="POST",
                headers={"Content-Type": "application/json", "User-Agent": "test-your-luck"},
            )
            urllib.request.urlopen(request, timeout=12).read()
        except Exception:
            pass

    threading.Thread(target=send, daemon=True).start()


def pull_board() -> None:
    global board_note, board_rows
    board_note = "loading"
    board_rows = []

    def load() -> None:
        global board_rows, board_note
        try:
            listing = urllib.request.Request(
                "https://mantledb.sh/v2/list/tyl-luck-board-7f3a",
                headers={"User-Agent": "test-your-luck"},
            )
            listed = json.loads(urllib.request.urlopen(listing, timeout=12).read().decode("utf-8"))
            rows = []
            for entry in listed.get("entries") or []:
                path = str(entry.get("path") or "")
                if not path.startswith("p/"):
                    continue
                got = urllib.request.urlopen(
                    urllib.request.Request(f"{BOARD_ROOT}/{path}", headers={"User-Agent": "test-your-luck"}),
                    timeout=12,
                )
                data = json.loads(got.read().decode("utf-8"))
                item = known_item(str(data.get("id") or ""))
                name = clean_name(str(data.get("name") or ""))
                if item is None or not name:
                    continue
                rows.append({"name": name, "item": item["name"], "rarity": int(item["rarity"]), "id": item["id"], "player": path[2:]})
            rows.sort(key=lambda row: row["rarity"], reverse=True)
            board_rows = rows
            board_note = "" if rows else "nobody yet"
        except Exception:
            board_note = "offline"

    threading.Thread(target=load, daemon=True).start()


def same_name(left: str, right: str) -> bool:
    return clean_name(left).casefold() == clean_name(right).casefold()


def name_taken(wanted: str) -> bool:
    ensure_player()
    listing = urllib.request.Request(
        "https://mantledb.sh/v2/list/tyl-luck-board-7f3a",
        headers={"User-Agent": "test-your-luck"},
    )
    listed = json.loads(urllib.request.urlopen(listing, timeout=12).read().decode("utf-8"))
    for entry in listed.get("entries") or []:
        path = str(entry.get("path") or "")
        if not path.startswith("p/") or path[2:] == player_id:
            continue
        got = urllib.request.urlopen(
            urllib.request.Request(f"{BOARD_ROOT}/{path}", headers={"User-Agent": "test-your-luck"}),
            timeout=12,
        )
        data = json.loads(got.read().decode("utf-8"))
        if same_name(str(data.get("name") or ""), wanted):
            return True
    return False


def ask_name() -> None:
    global username
    import tkinter.messagebox as messagebox
    import tkinter.simpledialog as simpledialog

    picked = simpledialog.askstring("name", "username", initialvalue=username, parent=root)
    if picked is None:
        return
    cleaned = clean_name(picked)
    if not cleaned:
        return
    if same_name(username, cleaned):
        username = cleaned
        store_progress()
        push_best()
        return

    def check() -> None:
        failed = False
        taken = False
        try:
            taken = name_taken(cleaned)
        except Exception:
            failed = True

        def apply() -> None:
            global username
            if failed:
                messagebox.showinfo("name", "offline", parent=root)
                return
            if taken:
                messagebox.showinfo("name", "that name is taken", parent=root)
                return
            username = cleaned
            store_progress()
            push_best()

        root.after(0, apply)

    threading.Thread(target=check, daemon=True).start()


def tap_reset() -> None:
    global reset_taps, money, roll_count, found, potion_until, speed_until, mega_left
    global clover_tier, autoclicker_owned, autoclicker_on, next_multi, spinning, pending_result
    global last_result, show_item, payout_until, roll_ready, land_zoom, land_zoom_target, peace_reveal
    global username, best_id, best_rarity, buff_count, super_buff_count
    reset_taps += 1
    if reset_taps < 10:
        return
    money = 0
    roll_count = 0
    found = {}
    potion_until = 0
    speed_until = 0
    mega_left = 0
    clover_tier = 0
    autoclicker_owned = False
    autoclicker_on = False
    next_multi = 1
    spinning = False
    pending_result = None
    last_result = None
    show_item = None
    payout_until = 0
    roll_ready = 0
    land_zoom = 1
    land_zoom_target = 1
    peace_reveal = 1
    particles.clear()
    reset_taps = 0
    username = ""
    best_id = ""
    best_rarity = 0
    buff_count = 0
    super_buff_count = 0
    store_progress()
    push_best()


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


def buy_clover() -> None:
    global money, clover_tier
    if clover_tier >= len(CLOVER_NAME):
        return
    cost = CLOVER_COST[clover_tier]
    if money < cost:
        return
    money -= cost
    clover_tier += 1
    store_progress()


def buy_autoclicker() -> None:
    global money, autoclicker_owned, autoclicker_on
    if not autoclicker_owned:
        if money < AUTO_COST:
            return
        money -= AUTO_COST
        autoclicker_owned = True
        autoclicker_on = True
    else:
        autoclicker_on = not autoclicker_on
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
        mci_cmd(f"setaudio track volume to {120 if mode == 'game' else 400}")


def play_tick() -> None:
    mci_cmd("stop tick")
    mci_cmd("play tick from 0")


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


def begin_roll(auto: bool = False) -> None:
    global spinning, pending_result, roll_items, roll_times, roll_started, roll_i
    global show_zoom, show_alpha, land_zoom, land_zoom_target, peace_reveal, roll_pad, mega_left
    global next_multi, money
    if spinning or bestiary_open or shop_open or time.perf_counter() < roll_ready:
        return
    if auto:
        if money < 3:
            return
        money -= 3
    boost = luck_now()
    if mega_left > 0:
        mega_left -= 1
        boost = 100
        store_progress()
    boost *= next_multi
    next_multi = 1
    pending_result = pick_rarity(boost)
    count = 40
    roll_items = [pick_rarity(boost) for _ in range(count - 2)]
    roll_items.append(pending_result)
    roll_times = []
    pace = speed_now() * 1.25 * gambler_pace()
    moment = 0.14 / pace
    roll_pad = 0.06 / pace
    for index in range(count):
        along = index / (count - 1)
        moment += (0.022 + (0.5 - 0.022) * (along ** 2.8)) / pace
        roll_times.append(moment)
    roll_started = time.perf_counter()
    roll_i = -1
    show_item = None
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
    global money, payout_shown, payout_until, next_multi, roll_ready, best_id, best_rarity, buff_count, super_buff_count
    if pending_result is None:
        spinning = False
        return
    spinning = False
    roll_ready = time.perf_counter() + 0.5
    last_result = pending_result
    roll_count += 1
    money += int(pending_result["rarity"])
    payout_shown = int(pending_result["rarity"])
    payout_until = time.perf_counter() + 1.4
    slot = found.get(pending_result["id"])
    if slot is None:
        found[pending_result["id"]] = {"count": 1, "first": roll_count}
    else:
        slot["count"] = int(slot.get("count", 0)) + 1
    if pending_result["id"] == "buff":
        buff_count += 1
    elif pending_result["id"] == "super buff":
        super_buff_count += 1
    if int(pending_result["rarity"]) > best_rarity:
        best_rarity = int(pending_result["rarity"])
        best_id = pending_result["id"]
        store_progress()
        push_best()
    else:
        store_progress()
    next_multi *= NEXT_MULTI.get(pending_result["id"], 1)
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
    if spinning and roll_times:
        elapsed = now - roll_started
        while roll_i + 1 < len(roll_items) and elapsed >= roll_times[roll_i + 1]:
            roll_i += 1
            show_item = roll_items[roll_i]
            show_zoom = 1.07
            show_alpha = 60
            play_tick()
        if roll_i >= len(roll_items) - 1 and elapsed >= roll_times[len(roll_items) - 1] + roll_pad:
            finish_roll()
    if autoclicker_on and not spinning and not bestiary_open and not shop_open and not board_open and mode == "game":
        if now >= roll_ready + 1.5 and money >= 3:
            begin_roll(True)
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
    if bestiary_open or shop_open or board_open:
        if shop_open and point_in(BUY_LUCK_BOX, x, y):
            return "buy"
        if shop_open and point_in(BUY_SPEED_BOX, x, y):
            return "buy-speed"
        if shop_open and point_in(BUY_MEGA_BOX, x, y):
            return "buy-mega"
        if shop_open and point_in(BUY_CLOVER_BOX, x, y):
            return "buy-clover"
        if shop_open and point_in(BUY_AUTO_BOX, x, y):
            return "buy-auto"
        return "back" if point_in(BACK_BOX, x, y) else None
    if point_in(ROLL_BOX, x, y):
        return "roll"
    if point_in(DEX_BOX, x, y):
        return "bestiary"
    if point_in(SHOP_BOX, x, y):
        return "shop"
    if point_in(BOARD_BOX, x, y):
        return "board"
    if point_in(NAME_BOX, x, y):
        return "name"
    if point_in(RESET_BOX, x, y):
        return "reset"
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


def text_span(text: str, font: ImageFont.FreeTypeFont, scale: float = 1.0) -> tuple[float, float]:
    box = font.getbbox(text)
    return (box[2] - box[0] + 8) * scale, (box[3] - box[1] + 8) * scale


def hovering_center(cx: float, cy: float, rarity: dict, font: ImageFont.FreeTypeFont, scale: float = 1.0) -> bool:
    width = max(text_span(rarity["odds"], font, scale)[0], text_span(rarity["chance"], font, scale)[0])
    height = max(text_span(rarity["odds"], font, scale)[1], text_span(rarity["chance"], font, scale)[1])
    return abs(pointer_x - cx) <= width / 2 and abs(pointer_y - cy) <= height / 2


def hovering_right(right: float, cy: float, rarity: dict, font: ImageFont.FreeTypeFont) -> bool:
    width = max(text_span(rarity["odds"], font)[0], text_span(rarity["chance"], font)[0])
    height = max(text_span(rarity["odds"], font)[1], text_span(rarity["chance"], font)[1])
    return right - width <= pointer_x <= right + 6 and abs(pointer_y - cy) <= height / 2


def shown_odds(rarity: dict, hovered: bool) -> str:
    return rarity["chance"] if hovered else rarity["odds"]


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
    odds_y = name_y + 44
    label = shown_odds(rarity, hovering_center(GAME_W / 2, odds_y, rarity, FONT_22, scale))
    paint_line(frame, label, FONT_22, rarity["color"], GAME_W / 2, odds_y, scale, alpha)


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
        paint_named(frame, diamond_face(), scale, int(alpha * (1 - peace_reveal)))
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
        screen_y = view_top + y + 14 - bestiary_scroll
        label = shown_odds(rarity, hovering_right(GAME_W - 88, screen_y, rarity, FONT_14))
        sheet_pen.text((GAME_W - 88, y + 14), label, font=FONT_14, fill=(210, 210, 210, 255), anchor="rm")
        sheet_pen.text((88, y + 34), f"earliest roll {slot['first']}", font=FONT_12, fill=(200, 200, 200, 255), anchor="lm")
        sheet_pen.text((GAME_W - 88, y + 34), f"got {slot['count']}", font=FONT_12, fill=(200, 200, 200, 255), anchor="rm")
    shown = sheet.crop((0, bestiary_scroll, GAME_W, bestiary_scroll + view_h))
    frame.paste(shown, (0, view_top), shown)
    paint_ui_button(frame, BACK_BOX, "back", held_name == "back", FONT_14)


def paint_board(frame: Image.Image) -> None:
    global board_scroll
    veil = Image.new("RGBA", (GAME_W, GAME_H), (16, 16, 18, 255))
    frame.alpha_composite(veil)
    pen = ImageDraw.Draw(frame)
    pen.text((GAME_W / 2, 36), "leaderboard", font=FONT_28, fill=(255, 255, 255, 255), anchor="mm")
    rows = list(board_rows)
    if board_note:
        pen.text((GAME_W / 2, 150), board_note, font=FONT_16, fill=(180, 180, 180, 255), anchor="mm")
    view_top = 68
    view_h = GAME_H - 132
    row_h = 36
    content_h = max(view_h, len(rows) * row_h)
    board_scroll = max(0, min(board_scroll, content_h - view_h))
    sheet = Image.new("RGBA", (GAME_W, content_h), (0, 0, 0, 0))
    sheet_pen = ImageDraw.Draw(sheet)
    for index, row in enumerate(rows):
        y = index * row_h + 16
        mine = row["player"] == player_id
        fill = (255, 214, 80, 255) if mine else (230, 230, 230, 255)
        sheet_pen.text((16, y), str(index + 1), font=FONT_14, fill=fill, anchor="lm")
        sheet_pen.text((48, y), row["name"], font=FONT_16, fill=fill, anchor="lm")
        item = known_item(row["id"])
        sheet_pen.text((250, y), row["item"], font=FONT_16, fill=item["color"] + (255,) if item else fill, anchor="lm")
        screen_y = view_top + y - board_scroll
        label = shown_odds(item, hovering_right(GAME_W - 16, screen_y, item, FONT_14)) if item else f"{row['rarity']:,}"
        sheet_pen.text((GAME_W - 16, y), label, font=FONT_14, fill=(210, 210, 210, 255), anchor="rm")
    shown = sheet.crop((0, board_scroll, GAME_W, board_scroll + view_h))
    frame.paste(shown, (0, view_top), shown)
    paint_ui_button(frame, BACK_BOX, "back", held_name == "back", FONT_14)


def paint_shop(frame: Image.Image) -> None:
    veil = Image.new("RGBA", (GAME_W, GAME_H), (16, 16, 18, 255))
    frame.alpha_composite(veil)
    pen = ImageDraw.Draw(frame)
    pen.text((GAME_W / 2, 36), "shop", font=FONT_28, fill=(255, 255, 255, 255), anchor="mm")
    pen.text((GAME_W / 2, 68), money_text(money), font=FONT_22, fill=(45, 230, 95, 255), anchor="mm")
    luck_x = GAME_W // 2 - 150
    speed_x = GAME_W // 2 + 150
    pen.text((luck_x, 100), "2x luck", font=FONT_22, fill=(255, 196, 64, 255), anchor="mm")
    pen.text((speed_x, 100), "2x speed", font=FONT_22, fill=(120, 210, 255, 255), anchor="mm")
    pen.text((luck_x, 118), "5 min", font=FONT_16, fill=(220, 220, 220, 255), anchor="mm")
    pen.text((speed_x, 118), "5 min", font=FONT_16, fill=(220, 220, 220, 255), anchor="mm")
    pen.text((luck_x, 134), "$375", font=FONT_16, fill=(45, 230, 95, 255), anchor="mm")
    pen.text((speed_x, 134), "$450", font=FONT_16, fill=(120, 210, 255, 255), anchor="mm")
    pen.text((luck_x, 196), "100x luck", font=FONT_22, fill=(255, 196, 64, 255), anchor="mm")
    pen.text((luck_x, 214), "next roll", font=FONT_16, fill=(220, 220, 220, 255), anchor="mm")
    pen.text((luck_x, 230), "$12,000", font=FONT_16, fill=(255, 196, 64, 255), anchor="mm")
    owned = clover_tier >= len(CLOVER_NAME)
    leaf = len(CLOVER_NAME) - 1 if owned else clover_tier
    pen.text((speed_x, 196), CLOVER_NAME[leaf], font=FONT_22, fill=(48, 180, 72, 255), anchor="mm")
    pen.text((speed_x, 214), CLOVER_NOTE[leaf], font=FONT_16, fill=(220, 220, 220, 255), anchor="mm")
    pen.text((speed_x, 230), "owned" if owned else money_text(CLOVER_COST[clover_tier]), font=FONT_16, fill=(48, 180, 72, 255), anchor="mm")
    pen.text((GAME_W / 2, 292), "autoclicker", font=FONT_22, fill=(255, 140, 80, 255), anchor="mm")
    pen.text((GAME_W / 2, 310), "$3 a roll", font=FONT_16, fill=(220, 220, 220, 255), anchor="mm")
    paint_ui_button(frame, BUY_LUCK_BOX, "buy", held_name == "buy" or money < POTION_COST, FONT_16)
    paint_ui_button(frame, BUY_SPEED_BOX, "buy", held_name == "buy-speed" or money < SPEED_COST, FONT_16)
    paint_ui_button(frame, BUY_MEGA_BOX, "buy", held_name == "buy-mega" or money < MEGA_COST, FONT_16)
    clover_held = owned or held_name == "buy-clover" or money < (0 if owned else CLOVER_COST[clover_tier])
    paint_ui_button(frame, BUY_CLOVER_BOX, "owned" if owned else "buy", clover_held, FONT_16)
    if autoclicker_owned:
        auto_label = "on" if autoclicker_on else "off"
        auto_held = held_name == "buy-auto"
    else:
        auto_label = "buy"
        auto_held = held_name == "buy-auto" or money < AUTO_COST
    paint_ui_button(frame, BUY_AUTO_BOX, auto_label, auto_held, FONT_16)
    paint_ui_button(frame, BACK_BOX, "back", held_name == "back", FONT_14)


def paint_luck_timer(frame: Image.Image) -> None:
    now = time.time()
    chips = []
    if speed_until > now:
        chips.append((f"2x  {potion_clock(speed_until - now)}", (120, 210, 255, 255)))
    if potion_until > now:
        chips.append((f"2x  {potion_clock(potion_until - now)}", (45, 230, 95, 255)))
    if mega_left > 0:
        if next_multi > 1:
            label = f"mega x{mega_left}"
        else:
            label = "100x next" if mega_left == 1 else f"100x x{mega_left}"
        chips.append((label, (255, 196, 64, 255)))
    if next_multi > 1:
        stacked = (100 if mega_left else luck_now()) * next_multi
        chips.append((f"{stacked}x next", (48, 220, 96, 255)))
    if clover_tier > 0:
        chips.append((f"{CLOVER_NAME[clover_tier - 1]} {CLOVER_NOTE[clover_tier - 1]}", (48, 180, 72, 255)))
    if buff_count:
        chips.append((f"buff +{buff_count}", (255, 196, 64, 255)))
    if super_buff_count:
        chips.append((f"super buff +{super_buff_count * 5}%", (186, 120, 255, 255)))
    title = gambler_name()
    if title:
        chips.append((title, (120, 210, 255, 255)))
    if autoclicker_on:
        chips.append(("auto", (255, 140, 80, 255)))
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
        wait = roll_ready - time.perf_counter()
        roll_held = held_name == "roll" or spinning or wait > 0
        label = "rolling" if spinning else f"{wait:.1f}" if wait > 0 else "roll"
        paint_ui_button(frame, ROLL_BOX, label, roll_held, FONT_16)
        paint_ui_button(frame, DEX_BOX, "bestiary", held_name == "bestiary", FONT_14)
        paint_ui_button(frame, SHOP_BOX, "shop", held_name == "shop", FONT_14)
        paint_ui_button(frame, BOARD_BOX, "board", held_name == "board", FONT_14)
        paint_ui_button(frame, NAME_BOX, username or "set name", held_name == "name", FONT_12)
        reset_label = "reset" if reset_taps == 0 else f"{reset_taps}/10"
        paint_ui_button(frame, RESET_BOX, reset_label, held_name == "reset", FONT_12)
    if bestiary_open:
        paint_bestiary(frame)
    if board_open:
        paint_board(frame)
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
    global held_start, held_name, bestiary_open, bestiary_scroll, shop_open, board_open, board_scroll
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
            board_open = False
            bestiary_scroll = 0
        elif chosen == "shop":
            shop_open = True
            bestiary_open = False
            board_open = False
        elif chosen == "board":
            board_open = True
            bestiary_open = False
            shop_open = False
            board_scroll = 0
            pull_board()
        elif chosen == "name":
            ask_name()
        elif chosen == "reset":
            tap_reset()
        elif chosen == "buy":
            buy_luck()
        elif chosen == "buy-speed":
            buy_speed()
        elif chosen == "buy-mega":
            buy_mega()
        elif chosen == "buy-clover":
            buy_clover()
        elif chosen == "buy-auto":
            buy_autoclicker()
        elif chosen == "back":
            bestiary_open = False
            shop_open = False
            board_open = False
    held_name = None


def close() -> None:
    mci_cmd("close hit")
    mci_cmd("close tick")
    mci_cmd("close track")
    root.destroy()


def preload() -> None:
    paths = [COMBO] if COMBO.exists() else []
    paths.extend(song_list())
    for path in paths:
        try:
            if path != COMBO:
                stripped(path)
            load_envelope(path)
        except Exception:
            pass


if len(WORDS) != len(BEATS_MS):
    raise RuntimeError("every beat needs a word")

if COMBO.exists():
    mci_cmd("close hit")
    mci_cmd(f'open "{COMBO}" type mpegvideo alias hit')
    mci_cmd("set hit time format milliseconds")

if TICK.exists():
    mci_cmd("close tick")
    mci_cmd(f'open "{TICK}" type waveaudio alias tick')

load_progress()
if username and best_id:
    push_best()
load_photos()
load_stars()
threading.Thread(target=preload, daemon=True).start()
def on_motion(event: tk.Event) -> None:
    global pointer_x, pointer_y
    pointer_x = event.x
    pointer_y = event.y


def on_wheel(event: tk.Event) -> None:
    global bestiary_scroll, board_scroll
    if mode == "game" and bestiary_open:
        bestiary_scroll = max(0, bestiary_scroll - event.delta // 6)
    elif mode == "game" and board_open:
        board_scroll = max(0, board_scroll - event.delta // 6)


canvas.bind("<Motion>", on_motion)
canvas.bind("<Button-1>", on_press)
canvas.bind("<ButtonRelease-1>", on_release)
canvas.bind("<MouseWheel>", on_wheel)
root.protocol("WM_DELETE_WINDOW", close)
draw()
root.after(200, start_intro)
root.mainloop()
