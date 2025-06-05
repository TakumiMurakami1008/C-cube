import json
import numpy as np
from pathlib import Path

import main


## パネル情報を管理するクラス
class PanelManager:
    def __init__(self, stage_num: int, config_path = Path("../Config") / "map_config.json", grid_shape= (400, 300)):
        # configからマップの基本情報を読み取り
        with open(config_path, 'r', encoding="utf-8_sig") as f:
            config = json.load(f)
        
        self.tile_width = config["tile_width"]
        self.tile_height = config["tile_height"]

        self._set_panels(stage_num = stage_num)

        self.panels_list = None

    def _set_panels(self, stage_num: int):
        """
        ファイルからタイルを設定
        """
        file_path = Path("../Config") / f"map_sample{stage_num}_config.json"
        # with open(f"map_stage{stage_num}.json", "r") as f:
        with open(file_path, "r", encoding="utf-8_sig") as f:
            map_data = json.load(f)

        # 緯度・経度の範囲を取得
        lat_min, lat_max = map_data["map_settings"]["latitude_range"]
        lon_min, lon_max = map_data["map_settings"]["longitude_range"]

        # グリッド数
        h, w = self.tile_height, self.tile_width

        panels_array = np.empty((h, w), dtype=object)

        # 緯度・経度 → グリッドインデックスに変換する関数
        def latlon_to_index(lat, lon):
            y = int((lat - lat_min) / (lat_max - lat_min) * (h - 1))
            x = int((lon - lon_min) / (lon_max - lon_min) * (w - 1))
            return y, x

        # 初期化
        for y in range(h):
            for x in range(w):
                panels_array[y, x] = None

        # 各 terrain ごとに設定
        for terrain in map_data["terrain"]:
            lat_start, lat_end = terrain["area"][0]
            lon_start, lon_end = terrain["area"][1]

            y0, _ = latlon_to_index(lat_start, lon_min)
            y1, _ = latlon_to_index(lat_end, lon_min)
            _, x0 = latlon_to_index(lat_min, lon_start)
            _, x1 = latlon_to_index(lat_min, lon_end)

            ground_strength = 1.0 - terrain["weakness"]
            terrain_type = terrain["type"]

            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    has_building = np.random.rand() > 0.3
                    building_strength = np.random.rand() if has_building else 0.0
                    shaking = 0.0

                    panel = main.Panel(
                        has_building=has_building,
                        building_strength=building_strength,
                        shaking=shaking,
                        ground_strength=ground_strength,
                        terrain_type=terrain_type
                    )
                    panels_array[y, x] = panel

        # 未設定エリアをデフォルトで埋める
        for y in range(h):
            for x in range(w):
                if panels_array[y, x] is None:
                    panels_array[y, x] = main.Panel(
                        has_building=False,
                        building_strength=0.0,
                        shaking=0.0,
                        ground_strength=0.5,
                        terrain_type="不明"
                    )

        self.panels = panels_array

    def simulate(self, max_disp):
        """
        各座標の max_disp[y, x] に基づき、建物が壊れるかを判定
        max_disp は self.tile_height x self.tile_width の NumPy配列である必要がある
        """
        if max_disp.shape != (self.tile_height, self.tile_width):
            raise ValueError(f"max_disp のサイズが一致しません。期待されたサイズ: ({self.tile_height}, {self.tile_width})\nmax_disp.shape: {max_disp.shape}")

        for y in range(self.tile_height):
            for x in range(self.tile_width):
                panel = self.panels[y, x]
                shaking = max_disp[y, x]
                panel.shaking = shaking

                # 建物がある & 強度 < 揺れ → 壊れる
                if panel.has_building and panel.building_strength < shaking:
                    panel.building_strength = -1  # 壊れた状態

        return self.panels
    
    def showPanelState(self, output_path="show_panel_state.json", show_limit=5):
        """
        パネルの状態をコンソールに表示するか、ファイルに出力
        - output_path: ファイルパスを指定するとJSONで出力
        - limit: コンソール出力の最大表示行数（多すぎると見づらくなるため）
        """

        panel_data = []
        for y in range(self.tile_height):
            for x in range(self.tile_width):
                panel = self.panels[y, x]
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

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(panel_data, f, ensure_ascii=False, indent=2)
            print(f"パネル情報を {output_path} に出力しました。")
        else:
            print("=== パネル状態の一部 ===")
            for i, data in enumerate(panel_data[:show_limit]):
                print(data)
            if len(panel_data) > show_limit:
                print(f"... ({len(panel_data) - show_limit}件省略)")
