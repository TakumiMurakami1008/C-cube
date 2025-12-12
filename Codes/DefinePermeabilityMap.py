import numpy as np

class DefinePermeabilityMap:
    def __init__(self, stage_data, panel_manager):
        self.stage_data = stage_data
        self.grid_width  = stage_data["map_settings"]["grid_size"]["width"]
        self.grid_height = stage_data["map_settings"]["grid_size"]["height"]
        self.terrain     = stage_data["terrain"]

        # マップを初期化（0=通りにくい）
        self.permeability_map = np.zeros((self.grid_height, self.grid_width), dtype=np.float32)

        self._generate_permeability_map(panel_manager)

    def _generate_permeability_map(self, panel_manager):
        panels = panel_manager.get_all_panels()
        for terrain in self.terrain:
            area = eval(terrain["area"])  # [[ymin, ymax],[xmin, xmax]]
            permeability = terrain["permeability"]

            y_min = int(area[0][0] * self.grid_height)
            y_max = int(area[0][1] * self.grid_height)
            x_min = int(area[1][0] * self.grid_width)
            x_max = int(area[1][1] * self.grid_width)

            self.permeability_map[y_min:y_max, x_min:x_max] = permeability
        
        # アイテムの効果判定
        for x in range(panel_manager.tile_width):
            for y in range(panel_manager.tile_height):
                panel = panels[x, y]
                if panel.item_id != -1:
                    if panel.item_id == 2:  # 防波堤アイテム
                        self.permeability_map[x, y] = 0.1 # 波の伝わりにくさ向上（一定）

    def get_permeability_map(self):
        return self.permeability_map