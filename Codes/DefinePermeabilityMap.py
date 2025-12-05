import numpy as np

class DefinePermeabilityMap:
    def __init__(self, stage_data):
        self.stage_data = stage_data
        self.grid_width  = stage_data["map_settings"]["grid_size"]["width"]
        self.grid_height = stage_data["map_settings"]["grid_size"]["height"]
        self.terrain     = stage_data["terrain"]

        # マップを初期化（0=通りにくい）
        self.permeability_map = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)

        self._generate_permeability_map()

    def _generate_permeability_map(self):
        for terrain in self.terrain:
            area = eval(terrain["area"])  # [[ymin, ymax],[xmin, xmax]]
            permeability = terrain["permeability"]

            y_min = int(area[0][0] * self.grid_height)
            y_max = int(area[0][1] * self.grid_height)
            x_min = int(area[1][0] * self.grid_width)
            x_max = int(area[1][1] * self.grid_width)

            self.permeability_map[y_min:y_max, x_min:x_max] = permeability

    def get_permeability_map(self):
        return self.permeability_map