from pathlib import Path

def greeting():
    return Path("assets/greeting.txt").read_text(encoding="utf-8").strip()
