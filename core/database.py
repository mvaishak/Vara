# JSON I/O for closet data
import os
import json
from typing import List, Dict

CLOSET_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'my_closet.json')
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'closet_images')
os.makedirs(IMAGES_DIR, exist_ok=True)

def load_closet_data() -> List[Dict]:
    try:
        if os.path.exists(CLOSET_FILE):
            with open(CLOSET_FILE, "r") as f:
                return json.load(f)
        return []
    except Exception:
        return []

def save_item(item_dict: dict, image_path: str) -> bool:
    try:
        closet_data = load_closet_data()
        item_dict = dict(item_dict)
        item_dict["image_path"] = image_path
        item_dict["id"] = len(closet_data)
        closet_data.append(item_dict)
        with open(CLOSET_FILE, "w") as f:
            json.dump(closet_data, f, indent=2)
        return True
    except Exception:
        return False
