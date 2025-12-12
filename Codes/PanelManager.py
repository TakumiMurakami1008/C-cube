import json
import numpy as np
import math
from pathlib import Path
import matplotlib.pyplot as plt
import ast  # 文字列を安全にPythonオブジェクトに変換するため

import main  # Panelクラスを使うため

# @dataclass
# class Panel: #パネル
#     building_type: int         # 建物の種類（例 0: なし, 1: 家, 2: ビル, ...）
#     building_strength: float   # 建物がある場合、建物の強度（0~1）、-1の場合壊れている建物とする
#     shaking: float             # 受けた地震の揺れの大きさ（例：加速度や震度）
#     waving: float              # 受けた津波の波の大きさ（例：波の高さ、勢い）
#     ground_strength: float     # 地盤の強さ（0〜1などで表現）
#     terrain_type: str          # 地形情報（例："hill", "plain", "coast", etc.）
#     item_id: int             # パネルに設置されているアイテムのID（-1ならなし）


class PanelManager:
    def __init__(self, stage_data, panel_origin=[]):
        self.tile_width = stage_data["map_settings"]["grid_size"]["width"]
        self.tile_height = stage_data["map_settings"]["grid_size"]["height"]
        self.panels_list = None
        self.panels = None
        self._set_panels(stage_data=stage_data, panel_origin=panel_origin)

    def _set_panels(self, stage_data, panel_origin=[]):
        if stage_data is None:
            raise ValueError("stage_data が指定されていません。")

        w, h = self.tile_width, self.tile_height
        panels_array = np.empty((w, h), dtype=object)  # (x, y)順

        for x in range(w):
            for y in range(h):
                panels_array[x, y] = None

        for terrain in stage_data["terrain"]:
            # area を文字列から配列に変換
            if isinstance(terrain["area"], str):
                area = ast.literal_eval(terrain["area"])
            else:
                area = terrain["area"]

            x0_ratio, x1_ratio = area[0]
            y0_ratio, y1_ratio = area[1]

            # print(f"設定中の地形: {terrain['type']} ({x0_ratio}, {y0_ratio}) to ({x1_ratio}, {y1_ratio})")

            # 割合 → グリッド番号
            x0 = int(math.floor(x0_ratio * w))
            x1 = int(math.ceil(x1_ratio * w))
            y0 = int(math.floor(y0_ratio * h))
            y1 = int(math.ceil(y1_ratio * h))

            # 範囲クリップ
            x0 = max(0, min(x0, w))
            x1 = max(0, min(x1, w))
            y0 = max(0, min(y0, h))
            y1 = max(0, min(y1, h))

            ground_strength = 1.0 - terrain["weakness"]
            terrain_type = terrain["type"]

            for x in range(x0, x1):
                for y in range(y0, y1):
                    shaking = 0
                    waving = 0
                    if panel_origin is not None and len(panel_origin) > 0:
                            # パネルがすでに設定されている場合は、地形情報を更新
                            panel = main.Panel(
                                building_type=panel_origin[x][y].building_type,
                                building_strength=panel_origin[x][y].building_strength,
                                shaking=shaking,
                                waving=waving,
                                ground_strength=ground_strength,
                                terrain_type=terrain_type,
                                item_id=panel_origin[x][y].item_id
                            )
                    else:
                        building_type = -1 # 建物なし
                        building_strength = 0
                        panel = main.Panel(
                            building_type=building_type,
                            building_strength=building_strength,
                            shaking=shaking,
                            waving=waving,
                            ground_strength=ground_strength,
                            terrain_type=terrain_type,
                            item_id=-1
                        )
                    panels_array[x, y] = panel

        # 未設定パネルをデフォルト値で初期化
        for x in range(w):
            for y in range(h):
                if panels_array[x, y] is None:
                    panels_array[x, y] = main.Panel(
                        building_type=-1,
                        building_strength=0.0,
                        shaking=0.0,
                        waving=0.0,
                        ground_strength=0.5,
                        terrain_type="不明",
                        item_id=-1
                    )

        self.panels = panels_array

    # def simulate(self, max_disp):
    #     if max_disp.shape != (self.tile_width, self.tile_height):
    #         raise ValueError(
    #             f"max_disp のサイズが一致しません。期待: ({self.tile_width}, {self.tile_height})\n実際: {max_disp.shape}"
    #         )

    #     for x in range(self.tile_width):
    #         for y in range(self.tile_height):
    #             panel = self.panels[x, y]
    #             shaking = max_disp[x, y]
    #             panel.shaking = shaking

    #             if panel.building_type < 0:
    #                 # 建物なしパネルはスキップ
    #                 self.panels[x, y] = panel
    #                 continue

    #             # 耐震性: 建物の強さ × 地盤の強さ × 係数
    #             alpha = 10.0 # 調整用係数
    #             resistance = panel.building_strength * panel.ground_strength * alpha

    #             # 建物あり & 揺れ > 耐震性 → 壊れる
    #             if shaking > resistance:
    #                 panel.building_strength = -1

    #             self.panels[x, y] = panel

    #     return self.panels

    # デバッグ用出力関数
    def showPanelState(self, output_path="../Debug_folder/show_panel_state.json", show_limit=5):
        panel_data = []
        shaking_map = np.zeros((self.tile_width, self.tile_height), dtype=float)

        for x in range(self.tile_width):
            for y in range(self.tile_height):
                panel = self.panels[x, y]
                data = {
                    "x": x,
                    "y": y,
                    "building_type": panel.building_type,
                    "building_strength": panel.building_strength,
                    "shaking": panel.shaking,
                    "ground_strength": panel.ground_strength,
                    "terrain_type": panel.terrain_type
                }
                panel_data.append(data)
                shaking_map[x, y] = panel.shaking

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
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

    # パネルを取得する関数
    def get_all_panels(self):
        return self.panels
    
    def set_all_panels(self, panels):
        self.panels = panels

    def get_panel(self, x, y):
        if 0 <= x < self.tile_width and 0 <= y < self.tile_height:
            return self.panels[x, y]
        else:
            raise IndexError(f"パネルのインデックスが範囲外です: ({x}, {y})")


if __name__ == "__main__":
    # JSONファイルから読み込み
    with open("../Config/map_sample2_config.json", "r", encoding="utf-8") as f:
        stage_data = json.load(f)

    panel_manager = PanelManager(stage_data=stage_data)
    # panel_manager.showPanelState(output_path="../Debug_folder/panel_state.json")
