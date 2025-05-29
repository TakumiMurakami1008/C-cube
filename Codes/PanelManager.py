import json
import numpy as np

from Codes.main import *
from Config import *



## パネル情報を管理するクラス
class PanelManager:
    def __init__(self, stage_num: int, config_path = "../Config.map_config.json", grid_shape= (400, 300)):
        # configからマップの基本情報を読み取り
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.tile_width = config["tile_width"]
        self.tile_height = config["tile_height"]

        self._set_panels(stage_num = stage_num)

        self.panels_list = None

    def _set_panels(self, stage_num: int):
        """
        ステージ用のパネルを設定する（地形マップを使用）
        """
        # 地形マップ情報を読み込み
        with open(f"map_stage{stage_num}.json", "r") as f:
            terrain_data = json.load(f)

        panels_array = np.empty((self.tile_height, self.tile_width), dtype=object)

        # 全体を初期化（未定義領域があればデフォルト地形として平地にする）
        for y in range(self.tile_height):
            for x in range(self.tile_width):
                panels_array[y, x] = None

        # 各地形ごとにパネルを設定
        for key, terrain in terrain_data.items():
            y_range = range(terrain["area"][0][0], terrain["area"][0][1] + 1)
            x_range = range(terrain["area"][1][0], terrain["area"][1][1] + 1)
            ground_strength = 1.0 - terrain["weakness"]
            terrain_type = terrain["type"]

            for y in y_range:
                for x in x_range:
                    # 
                    has_building = np.random.rand() > 0.3
                    building_strength = np.random.rand() if has_building else 0.0
                    shaking = 0.0

                    panel = Panel(
                        has_building=has_building,
                        building_strength=building_strength,
                        shaking=shaking,
                        ground_strength=ground_strength,
                        terrain_type=terrain_type
                    )
                    panels_array[y, x] = panel

        # Noneのまま残っているパネル（範囲外）にデフォルト値を入れる（地形: "不明", 地盤強度: 0.5）
        for y in range(self.tile_height):
            for x in range(self.tile_width):
                if panels_array[y, x] is None:
                    panel = Panel(
                        has_building=False,
                        building_strength=0.0,
                        shaking=0.0,
                        ground_strength=0.5,
                        terrain_type="不明"
                    )
                    panels_array[y, x] = panel

        return panels_array



    def simulate(self, max_disp):
        """
        各座標の max_disp[y, x] に基づき、建物が壊れるかを判定
        max_disp は self.tile_height x self.tile_width の NumPy配列である必要がある
        """
        if max_disp.shape != (self.tile_height, self.tile_width):
            raise ValueError(f"max_disp のサイズが一致しません。期待されたサイズ: ({self.tile_height}, {self.tile_width})")

        for y in range(self.tile_height):
            for x in range(self.tile_width):
                panel = self.panels[y, x]
                shaking = max_disp[y, x]
                panel.shaking = shaking

                # 建物がある & 強度 < 揺れ → 壊れる
                if panel.has_building and panel.building_strength < shaking:
                    panel.building_strength = -1  # 壊れた状態

        return self.panels
