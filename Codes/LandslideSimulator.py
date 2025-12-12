## 土砂災害シミュレーター関数
# - 雨天時、または一定以上の揺れがある場合に、山地から土砂崩れが発生
# - 土砂崩れは一定半径内の平地や台地に被害を及ぼし、建物を破壊
import math
import random

class LandslideSimulator:
    def __init__(self, panel_manager, stage_data, damage_radius=2, shaking_threshold=5.0):
        """
        Args:
            panel_manager: PanelManagerインスタンス
            stage_data: ステージ設定データ（天気情報 weather を含むことを想定）
            damage_radius: 被害半径
            shaking_threshold: 土砂崩れが発生する震度（shaking）の閾値
        """
        self.updated_panels = None
        self.tile_width = panel_manager.tile_width
        self.tile_height = panel_manager.tile_height
        self.damage_radius = damage_radius
        self.shaking_threshold = shaking_threshold

        # Configに天気がない場合のデフォルト値（ランダム or 晴れ）
        if "weather" in stage_data:
            self.weather = stage_data["weather"]
        else:
            # Configになければ50%で雨にするなどの仮処理
            self.weather = "Rain" if random.random() < 0.5 else "Sunny"
            print(f"※天気情報がConfigに見つからないため、ランダム設定しました: {self.weather}")

        # 防災施設（法面工事）とみなす建物ID
        # ※building_config.json にも追記が必要
        self.PROTECTION_BUILDING_IDs = (1,3)  # 例: 1と3を法面工事とみなす

    def run(self, panel_manager, shaking_map):
        """
        土砂災害シミュレーションを実行し、盤面を更新する
        Returns:
            int: 発生件数
        """
        panels = panel_manager.get_all_panels()
        landslide_sources = []

        # --- 1. 発生源の特定 ---
        for x in range(self.tile_width):
            for y in range(self.tile_height):
                panel = panels[x, y]
                
                # パネルがない、または地形情報がない場合はスキップ
                if panel is None or panel.terrain_type is None:
                    continue

                # 条件A: 地形が「山地」であること (JSONの定義と完全一致させる)
                if panel.terrain_type != "山地":
                    continue

                # 条件B: 防災施設（法面工事）がないこと
                if panel.building_type in self.PROTECTION_BUILDING_IDs:
                    continue

                if panel.item_id != -1: # TODO:土砂災害防止アイテムがある場合はスキップ
                    if panel.item_id == -1:  # 土砂災害防止アイテムID
                        continue

                # 条件C: 発生トリガー（雨 または 一定以上の揺れ）
                is_raining = (self.weather == "Rain")
                current_shaking = shaking_map[x, y]
                is_strong_shaking = (current_shaking >= self.shaking_threshold)

                if is_raining or is_strong_shaking:
                    landslide_sources.append((x, y))

        # --- 2. 被害の適用 ---
        affected_count = 0
        for src_x, src_y in landslide_sources:
            # 半径探索
            min_x = max(0, src_x - self.damage_radius)
            max_x = min(self.tile_width, src_x + self.damage_radius + 1)
            min_y = max(0, src_y - self.damage_radius)
            max_y = min(self.tile_height, src_y + self.damage_radius + 1)

            for tx in range(min_x, max_x):
                for ty in range(min_y, max_y):
                    # 発生源自体はスキップ（必要に応じて変更）
                    if tx == src_x and ty == src_y:
                        continue
                    
                    # 距離判定
                    dist = math.sqrt((tx - src_x)**2 + (ty - src_y)**2)
                    if dist <= self.damage_radius:
                        target_panel = panels[tx, ty]
                        if target_panel is None:
                            continue

                        # 山地以外の場所（平地や台地など）に被害を及ぼす
                        # または、そこに建物があれば種類問わず破壊する
                        if target_panel.building_type != -1:
                            # 既に倒壊していなければ
                            if target_panel.building_strength != -1:
                                # 法面工事されている場合は壊れない設定
                                if target_panel.building_type in self.PROTECTION_BUILDING_IDs:
                                    continue
                                
                                # 倒壊
                                target_panel.building_strength = -1
                                affected_count += 1
                                # print(f"土砂崩れ被害発生: ({tx}, {ty})")
                        panels[tx, ty] = target_panel
        
        self.updated_panels = panels
        return affected_count

    # パネル情報の更新（シミュレーション実行後の呼び出しを想定）
    def update_panels(self, panel_manager):
        """
            シミュレーション結果に基づき、パネルの情報を更新する
            
            Parameters:
                panel_manager (PanelManager): パネル管理オブジェクト
                panels: 更新後のパネル情報の2D配列

            Returns:
                panel_manager: 更新後のパネル情報を持つPanelManagerオブジェクト
        """
        panel_manager.set_all_panels(self.updated_panels)
        return panel_manager