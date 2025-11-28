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
        self.panel_manager = panel_manager
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
        self.PROTECTION_BUILDING_ID = 3 

    def run(self, shaking_map):
        """
        土砂災害シミュレーションを実行し、盤面を更新する
        Returns:
            int: 発生件数
        """
        panels = self.panel_manager.get_all_panels()
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
                if panel.building_type == self.PROTECTION_BUILDING_ID:
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
                                # 法面工事自体は壊れない設定
                                if target_panel.building_type == self.PROTECTION_BUILDING_ID:
                                    continue
                                
                                # 強制倒壊
                                target_panel.building_strength = -1
                                affected_count += 1
                                # ログなど（必要であれば）
                                # print(f"土砂崩れ被害: ({tx}, {ty})")

        print(f"土砂災害レポート: 天気={self.weather}, 発生源={len(landslide_sources)}箇所, 被害建物={affected_count}棟")
        return len(landslide_sources)