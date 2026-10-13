import json
import sys
import time
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
PHOTO = ROOT / "photos"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
SIZE = 640
RADIUS = 64

QUERIES = {
    "1": "United States one dollar bill",
    "2": "United States twenty dollar bill",
    "3": "United States one hundred dollar bill",
    "4": "silver bullion coin",
    "5": "gold bullion coins",
    "6": "physical bitcoin coin",
    "7": "bitcoin coin in hand",
    "8": "gold bitcoin coin",
    "9": "stacked bitcoin coins",
    "tiny": "miniature dollhouse",
    "medium": "medium coffee cup",
    "splash": "water splash",
    "fire": "bonfire flames",
    "lucky": "four leaf clover",
    "super lucky": "five leaf clover",
    "ultra lucky": "777 sign",
    "yin yang": "yin yang symbol",
    "fulgurite": "fulgurite lightning glass",
    "kintsugi": "kintsugi bowl",
    "orrery": "orrery solar system",
    "antikythera": "antikythera mechanism",
    "astrolabe": "astrolabe instrument",
    "fluorite": "fluorite crystal",
    "nautilus": "nautilus shell",
    "lodestone": "lodestone magnet",
    "mycelium": "mycelium",
    "bioluminescence": "bioluminescent plankton",
    "kaleidoscope": "kaleidoscope",
    "sundial": "sundial",
    "copal": "copal resin amber",
    "tesla": "tesla coil",
    "dichroic": "dichroic glass",
    "jet": "jet stone gem",
    "brinicle": "brinicle underwater ice",
    "lenticular": "lenticular cloud",
    "mammatus": "mammatus clouds",
    "catatumbo": "catatumbo lightning",
    "sailing stone": "sailing stone racetrack",
    "blood falls": "blood falls antarctica",
    "darvaza": "darvaza gas crater",
    "richat": "richat structure sahara",
    "socotra": "socotra dragon blood tree",
    "hoag": "hoag object galaxy",
    "crab nebula": "crab nebula",
    "pillars": "pillars of creation",
    "cartwheel": "cartwheel galaxy",
    "heat death": "deep space stars",
    "🐉": "chinese dragon statue",
    "🦄": "origami unicorn",
    "🌈": "rainbow sky",
    "🔥": "campfire flames",
    "💎": "diamond gemstone",
    "👑": "gold crown",
    "⚡": "lightning bolt",
    "🌟": "bright star night",
    "🌙": "crescent moon",
    "🍀": "four leaf clover",
    "💰": "money bag cash",
    "🎲": "dice",
    "🏆": "world cup trophy",
    "💀": "human skull",
    "👻": "sheet ghost halloween",
    "🎃": "jack o lantern",
    "🌸": "cherry blossom",
    "🌺": "hibiscus flower",
    "🍄": "mushroom",
    "🦋": "butterfly",
    "🐝": "honeybee",
    "🦊": "red fox",
    "🐼": "giant panda",
    "🐨": "koala",
    "🦁": "lion",
    "🐯": "tiger",
    "🐸": "frog",
    "🐙": "octopus",
    "🦈": "shark",
    "🐳": "whale",
    "🦅": "bald eagle",
    "🦉": "owl",
    "🌵": "cactus",
    "🌋": "volcano eruption",
    "🌊": "ocean wave",
    "🍎": "red apple",
    "🍒": "cherries bowl",
    "🍇": "grapes",
    "🍓": "strawberry",
    "🍕": "pizza",
    "🍩": "doughnut",
    "🎂": "birthday cake",
    "⚽": "soccer ball",
    "🏀": "basketball",
    "🎮": "video game controller",
    "🚀": "rocket launch",
    "🪐": "saturn planet",
    "💫": "shooting star",
    "🔮": "crystal ball",
    "💍": "diamond ring",
}


def photo_set(item_id: str) -> str:
    total = sum(ord(char) for char in item_id)
    return f"set-{(total % 5) + 1}"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read()


def hits(query: str) -> list[tuple[str, str]]:
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": query, "page_size": 8})
    data = json.loads(fetch(url))
    found = []
    for item in data.get("results", []):
        src = item.get("url") or ""
        if not src or item.get("filetype") == "svg":
            continue
        if (item.get("width") or 0) < 300:
            continue
        found.append((item.get("title") or "", src))
    return found


def square(raw: bytes) -> Image.Image:
    image = Image.open(BytesIO(raw)).convert("RGB")
    side = min(image.size)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    image = image.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (SIZE, SIZE), (16, 16, 18))
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, SIZE - 1, SIZE - 1), radius=RADIUS, fill=255)
    canvas.paste(image, (0, 0), mask)
    return canvas


def main() -> None:
    ok = 0
    for item_id, query in QUERIES.items():
        dest = PHOTO / photo_set(item_id) / f"{item_id}.jpg"
        saved = False
        try:
            choices = hits(query)
        except Exception as exc:
            print("search", item_id, type(exc).__name__, flush=True)
            time.sleep(1.2)
            choices = []
        for title, src in choices[:5]:
            lowered = title.lower()
            if any(word in lowered for word in ("icon", "emoji", "diagram", "map of")):
                continue
            try:
                square(fetch(src)).save(dest, "JPEG", quality=86)
                print("ok", item_id, title[:70], flush=True)
                ok += 1
                saved = True
                break
            except Exception as exc:
                print("skip", item_id, type(exc).__name__, flush=True)
                if type(exc).__name__ == "HTTPError":
                    time.sleep(1.5)
        if not saved:
            print("FAIL", item_id, flush=True)
        time.sleep(0.25)
    print("saved", ok, "of", len(QUERIES), flush=True)


if __name__ == "__main__":
    main()
