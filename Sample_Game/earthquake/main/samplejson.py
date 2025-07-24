import json
from pathlib import Path

path = Path("../Config") / f"map_sample.json"
with open(path, "r", encoding="utf-8_sig") as f:
    map_sample = json.load(f)
    map_settings = map_sample["map_settings"]
    latitiude = map_settings["latitude_range"] 
    longtitude = map_settings["longitude_range"]

    map_terrain = map_sample["terrain"]
    terrain_size = len(map_terrain)

    terrain_num = [None] * terrain_size

    for i in range(terrain_size):
        get_terrain = map_terrain[i]

        area_x_start = get_terrain["area"][0][0]

        print(get_terrain["area"])
        print(area_x_start)
        print(type(get_terrain["area"]))

        # print(get_terrain["weakness"])
        # print(type(get_terrain["weakness"]))
        

#tile_width,tile_height ... タイルの枚数

# print(latitiude)
# print(map_terrain)
# print(terrain_size)

print(terrain_num[1])