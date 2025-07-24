import json
from pathlib import Path

path = Path("../Config") / f"building_config.json"
with open(path, "r", encoding="utf-8_sig") as f:
    building = json.load(f)
    for i in range(3):
        building_num = building[str(i)]

        print(building_num)
        print(building_num["name"])