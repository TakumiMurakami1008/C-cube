import numpy as np

class DefineEpicenter:
    @staticmethod
    def define_epicenter(stage_data: dict) -> tuple:
        """
        ステージのJSONデータから震源を1点サンプリングして返す。
        線分の始点・終点は「マップの割合（0〜1）」で指定し、
        出力はグリッド番号（整数）で返す。

        Args:
            stage_data (dict): JSONから読み込んだステージ設定データ

        Returns:
            (grid_y, grid_x)  # グリッド番号
        """

        epicenter_config = stage_data.get("epicenter_distribution", {})

        # --- マップ設定の取得 ---
        map_settings = stage_data.get("map_settings", {})
        grid_size = map_settings.get("grid_size", {})
        grid_width  = grid_size.get("width")
        grid_height = grid_size.get("height")
        if not grid_width or not grid_height:
            raise ValueError("map_settings.grid_size の width / height が定義されていません。")

        # --- 割合で指定された線分の始点と終点 ---
        line_segment = epicenter_config.get("line_segment")
        if not line_segment or "start" not in line_segment or "end" not in line_segment:
            raise ValueError("epicenter_distribution に line_segment の start/end が定義されていません。")

        start_ratio = np.array(line_segment["start"], dtype=float)  # (y_ratio, x_ratio)
        end_ratio   = np.array(line_segment["end"], dtype=float)

        # --- 割合をグリッド座標に変換 ---
        start_grid = start_ratio * np.array([grid_height, grid_width])
        end_grid   = end_ratio   * np.array([grid_height, grid_width])

        # --- 共分散（なければデフォルト値） ---
        cov_along = epicenter_config.get("covariance_along_line", 1.0)
        cov_perp  = epicenter_config.get("covariance_perpendicular", 0.1)

        # --- 線分ベクトルと直交ベクトル ---
        line_vec = end_grid - start_grid
        line_length = np.linalg.norm(line_vec)
        line_dir = line_vec / line_length
        perp_dir = np.array([-line_dir[1], line_dir[0]])  # 線分に直交する方向

        # --- サンプリング ---
        t_along = np.clip(np.random.normal(loc=0.5, scale=np.sqrt(cov_along)), 0.0, 1.0)
        t_perp  = np.random.normal(loc=0.0, scale=np.sqrt(cov_perp))

        # --- 震源座標（グリッド番号）を計算 ---
        point_on_line = start_grid + t_along * line_vec
        offset = t_perp * perp_dir
        sampled_point = point_on_line + offset

        # --- 整数のグリッド番号に変換 ---
        grid_y = int(round(sampled_point[0]))
        grid_x = int(round(sampled_point[1]))

        # 範囲外クリップ
        grid_y = max(0, min(grid_height - 1, grid_y))
        grid_x = max(0, min(grid_width - 1, grid_x))

        return (grid_y, grid_x)


if __name__ == "__main__":
    stage_data = {
        "map_settings": {
            "grid_size": {
                "width": 50,
                "height": 50
            }
        },
        "epicenter_distribution": {
            "line_segment": {
                "start": [0.1, 0.1],  # 割合 (y, x)
                "end": [0.8, 0.9]
            },
            "covariance_along_line": 0.05,
            "covariance_perpendicular": 0.02
        }
    }

    epicenter = DefineEpicenter.define_epicenter(stage_data)
    print("震源位置（grid_y, grid_x）:", epicenter)
    # 例: 震源位置（grid_y, grid_x）: (29, 32)