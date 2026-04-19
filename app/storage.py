import json
import os
from typing import List, Dict

DATA_FILE = "data/history.json"


def ensure_storage():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def read_history() -> List[Dict]:
    ensure_storage()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_to_history(item: Dict):
    ensure_storage()
    history = read_history()
    history.append(item)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)