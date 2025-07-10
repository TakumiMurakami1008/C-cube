import numpy as np
import json

class DefineWeaknessMap:
    def __init__(self, stage_data):
        self.stage_data = stage_data
        self.grid_width = stage_data["map_settings"]["grid_size"]["width"]
        self.grid_height = stage_data["map_settings"]["grid_size"]["height"]
        self.terrain = stage_data["terrain"]
        self.weakness_map = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)
        self._generate_weakness_map()

    def _generate_weakness_map(self):
        for terrain in self.terrain:
            area = eval(terrain["area"])  # area: [[ymin, ymax], [xmin, xmax]]
            weakness = terrain["weakness"]

            y_min = int(area[0][0] * self.grid_height)
            y_max = int(area[0][1] * self.grid_height)
            x_min = int(area[1][0] * self.grid_width)
            x_max = int(area[1][1] * self.grid_width)

            self.weakness_map[y_min:y_max, x_min:x_max] = weakness

    def get_weakness_map(self):
        return self.weakness_map
