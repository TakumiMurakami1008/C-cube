import json
import numpy as np
import math
from pathlib import Path
import matplotlib.pyplot as plt

import main

class PanelManager:
    def __init__(self, map_data, stage_data):
        self.tile_width = map_data["grid_width"]
        self.tile_height = map_data["grid_height"]
        self._set_panels(stage_data=stage_data)
        self.panels_list = None

    def _set_panels(self, stage_data=None):
        if stage_data is None:
            raise ValueError("stage_data が指定されていません。")

        w, h = self.tile_width, self.tile_height
        panels_array = np.empty((w, h), dtype=object)  # <== (x, y)順

        for x in range(w):
            for y in range(h):
                panels_array[x, y] = None

        for terrain in stage_data["terrain"]:
            x0_ratio, x1_ratio = terrain["area"][0]
            y0_ratio, y1_ratio = terrain["area"][1]

            print(f"設定中の地形: {terrain['type']} ({x0_ratio}, {y0_ratio}) to ({x1_ratio}, {y1_ratio})")

            x0 = int(math.floor(x0_ratio * w))
            x1 = int(math.ceil(x1_ratio * w))
            y0 = int(math.floor(y0_ratio * h))
            y1 = int(math.ceil(y1_ratio * h))

            x0 = max(0, min(x0, w))
            x1 = max(0, min(x1, w))
            y0 = max(0, min(y0, h))
            y1 = max(0, min(y1, h))

            ground_strength = 1.0 - terrain["weakness"]
            terrain_type = terrain["type"]

            for x in range(x0, x1):
                for y in range(y0, y1):
                    building_type = 0
                    building_strength = 0
                    shaking = 0

                    panel = main.Panel(
                        building_type=building_type,
                        building_strength=building_strength,
                        shaking=shaking,
                        ground_strength=ground_strength,
                        terrain_type=terrain_type
                    )
                    panels_array[x, y] = panel

        for x in range(w):
            for y in range(h):
                if panels_array[x, y] is None:
                    panels_array[x, y] = main.Panel(
                        has_building=False,
                        building_strength=0.0,
                        shaking=0.0,
                        ground_strength=0.5,
                        terrain_type="不明"
                    )

        self.panels = panels_array

    def simulate(self, max_disp):
        if max_disp.shape != (self.tile_width, self.tile_height):
            raise ValueError(f"max_disp のサイズが一致しません。期待: ({self.tile_width}, {self.tile_height})\n実際: {max_disp.shape}")

        for x in range(self.tile_width):
            for y in range(self.tile_height):
                panel = self.panels[x, y]
                shaking = max_disp[x, y]
                panel.shaking = shaking

                alpha = 0.5  # 地震の影響を調整する係数

                # 耐震性: 建物の強さ × 地盤の強さ
                resistance = panel.building_strength * panel.ground_strength * alpha

                # 建物あり & 揺れ > 耐震性 → 壊れる
                if panel.building_type > 0 and shaking > resistance:
                    panel.building_strength = -1  # 壊れた建物

                self.panels[x, y] = panel

        return self.panels

    def showPanelState(self, output_path="../Debug_folder/show_panel_state.json", show_limit=5):
        '''
        パネルの状態を表示する（受けた震度：max_disp）
        '''
        panel_data = []
        shaking_map = np.zeros((self.tile_width, self.tile_height), dtype=float)

        for x in range(self.tile_width):
            for y in range(self.tile_height):
                panel = self.panels[x, y]
                data = {
                    "x": x,
                    "y": y,
                    "has_building": panel.has_building,
                    "building_strength": panel.building_strength,
                    "shaking": panel.shaking,
                    "ground_strength": panel.ground_strength,
                    "terrain_type": panel.terrain_type
                }
                panel_data.append(data)
                shaking_map[x, y] = panel.shaking

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(panel_data, f, ensure_ascii=False, indent=2)
            print(f"パネル情報を {output_path} に出力しました。")

        fig, ax = plt.subplots(figsize=(8, 6))
        im = ax.imshow(shaking_map.T, cmap='hot', interpolation='nearest', origin='upper')
        ax.set_title("Shaking Intensity Map")
        plt.colorbar(im, ax=ax, label="Shaking")

        image_output_path = Path(output_path).with_name("shaking_map.png")
        plt.savefig(image_output_path, dpi=150, bbox_inches='tight')
        print(f"shaking カラーマップ画像を {image_output_path} に保存しました。")

        plt.show()



if __name__ == "__main__":
    # デバッグ用のパネルマネージャーを作成
    map_data = {
        "grid_width": 10,
        "grid_height": 10
    }
    
    stage_data = {
        "terrain": [
            {
                "type": "plain",
                "weakness": 0.1,
                "area": [[0, 9], [0, 9]]
            }
        ]
    }

    panel_manager = PanelManager(map_data=map_data, stage_data=stage_data)
    panels = panel_manager.simulate(max_disp=np.random.rand(10, 10) * 100)
    panel_manager.showPanelState()