import numpy as np

class DefineEpicenter:
    @staticmethod

    def get_stage_data(stage_data: dict) -> tuple:

        epicenter_config = stage_data.get("epicenter_distribution", {})

        # --- マップ設定の取得 ---
        map_settings = stage_data.get("map_settings", {})
        grid_size = map_settings.get("grid_size", {})
        grid_width  = grid_size.get("width")
        grid_height = grid_size.get("height")

        return (epicenter_config, grid_width, grid_height)

    def calcrate_line(stage_data):
        if not stage_data[1] or not stage_data[2]:
            raise ValueError("map_settings.grid_size の width / height が定義されていません。")

        # --- 割合で指定された線分の始点と終点 ---
        line_segment = stage_data[0].get("line_segment")
        if not line_segment or "start" not in line_segment or "end" not in line_segment:
            raise ValueError("epicenter_distribution に line_segment の start/end が定義されていません。")

        start_ratio = np.array(line_segment["start"], dtype=float)  # (y_ratio, x_ratio)
        end_ratio   = np.array(line_segment["end"], dtype=float)

        # --- 割合をグリッド座標に変換 ---
        start_grid = start_ratio * np.array([stage_data[2], stage_data[1]])
        end_grid   = end_ratio   * np.array([stage_data[2], stage_data[1]])

        # # --- 共分散（なければデフォルト値） ---
        # cov_along = stage_data[0].get("covariance_along_line", 1.0)
        # cov_perp  = stage_data[0].get("covariance_perpendicular", 0.1)

        # # --- 線分ベクトルと直交ベクトル ---
        # line_vec = end_grid - start_grid
        # line_length = np.linalg.norm(line_vec)
        # line_dir = line_vec / line_length
        # perp_dir = np.array([-line_dir[1], line_dir[0]])  # 線分に直交する方向

        # # --- サンプリング ---
        # t_along = np.clip(np.random.normal(loc=0.5, scale=np.sqrt(cov_along)), 0.0, 1.0)
        # t_perp  = np.random.normal(loc=0.0, scale=np.sqrt(cov_perp))

        # # --- 震源座標（グリッド番号）を計算 ---
        # point_on_line = start_grid + t_along * line_vec
        # offset = t_perp * perp_dir
        # sampled_point = point_on_line + offset

        return (start_grid, end_grid)
    
    def calcrate_area(stage_data):
        if not stage_data[1] or not stage_data[2]:
            raise ValueError("map_settings.grid_size の width / height が定義されていません。")

        # --- 割合で指定された線分の始点と終点 ---
        line_segment = stage_data[0].get("line_segment")
        if not line_segment or "start" not in line_segment or "end" not in line_segment:
            raise ValueError("epicenter_distribution に line_segment の start/end が定義されていません。")

        start_ratio = np.array(line_segment["start"], dtype=float)  # (y_ratio, x_ratio)
        end_ratio   = np.array(line_segment["end"], dtype=float)

        # --- 割合をグリッド座標に変換 ---
        start_grid = start_ratio * np.array([stage_data[2], stage_data[1]])
        end_grid   = end_ratio   * np.array([stage_data[2], stage_data[1]])

        print("start_grid = " + str(start_grid))
        print("end_grid = " + str(end_grid))

        # --- 共分散（なければデフォルト値） ---
        cov_along = stage_data[0].get("covariance_along_line", 1.0)
        cov_perp  = stage_data[0].get("covariance_perpendicular", 0.1)

        # --- 線分ベクトルと直交ベクトル ---
        line_vec = end_grid - start_grid
        line_length = np.linalg.norm(line_vec)
        line_dir = line_vec / line_length
        perp_dir = np.array([-line_dir[1], line_dir[0]])  # 線分に直交する方向

        t_along_max = 0.5 + np.sqrt(cov_along)
        t_along_min = 0.5 - np.sqrt(cov_along)

        t_perp_max = 0.0 + np.sqrt(cov_perp)
        t_perp_min = 0.0 - np.sqrt(cov_perp)

        # print("t_al_max " + str(t_along_max))
        # print("t_al_min " + str(t_along_min))

        # print("t_pe_max " + str(t_perp_max))
        # print("t_pe_min " + str(t_perp_min))

        # point_on_line_1 = start_grid + t_along_max * line_vec
        # offset_1 = t_perp_max * perp_dir
        # sampled_point_1 = point_on_line_1 + offset_1

        # point_on_line_2 = start_grid + t_along_max * line_vec
        # offset_2 = t_perp_min * perp_dir
        # sampled_point_2 = point_on_line_2 + offset_2

        # point_on_line_3 = start_grid + t_along_min * line_vec
        # offset_3 = t_perp_max * perp_dir
        # sampled_point_3 = point_on_line_3 + offset_3

        # point_on_line_4 = start_grid + t_along_min * line_vec
        # offset_4 = t_perp_min * perp_dir
        # sampled_point_4 = point_on_line_4 + offset_4

        point_on_line_1 = start_grid + t_along_max * line_vec
        offset_1 = t_perp_max * perp_dir
        sampled_point_1 = point_on_line_1 + offset_1 + (1, 1)

        point_on_line_2 = start_grid + t_along_max * line_vec
        offset_2 = t_perp_min * perp_dir
        sampled_point_2 = point_on_line_2 + offset_2 + (1, -1)

        point_on_line_3 = start_grid + t_along_min * line_vec
        offset_3 = t_perp_max * perp_dir
        sampled_point_3 = point_on_line_3 + offset_3 + (-1, 1)

        point_on_line_4 = start_grid + t_along_min * line_vec
        offset_4 = t_perp_min * perp_dir
        sampled_point_4 = point_on_line_4 + offset_4 + (-1, -1)

        # point_on_line_1 = start_grid + t_along_max * line_vec
        # offset_1 = t_perp_max * perp_dir
        # sampled_point_1 = point_on_line_1 + offset_1 + (-1, 1)

        # point_on_line_2 = start_grid + t_along_max * line_vec
        # offset_2 = t_perp_min * perp_dir
        # sampled_point_2 = point_on_line_2 + offset_2 + (1, 1)

        # point_on_line_3 = start_grid + t_along_min * line_vec
        # offset_3 = t_perp_max * perp_dir
        # sampled_point_3 = point_on_line_3 + offset_3 + (-1, -1)

        # point_on_line_4 = start_grid + t_along_min * line_vec
        # offset_4 = t_perp_min * perp_dir
        # sampled_point_4 = point_on_line_4 + offset_4 + (1, -1)

        print("sample_point_1 " + str(sampled_point_1))
        print("sample_point_2 " + str(sampled_point_2))
        print("sample_point_3 " + str(sampled_point_3))
        print("sample_point_4 " + str(sampled_point_4))

        return (sampled_point_1, sampled_point_2, sampled_point_3, sampled_point_4)


    def define_epicenter(line, stage_data):
        """
        ステージのJSONデータから震源を1点サンプリングして返す。
        線分の始点・終点は「マップの割合（0〜1）」で指定し、
        出力はグリッド番号（整数）で返す。

        Args:
            stage_data (dict): JSONから読み込んだステージ設定データ

        Returns:
            (grid_y, grid_x)  # グリッド番号
        """

        # epicenter_config = stage_data.get("epicenter_distribution", {})

        # # --- マップ設定の取得 ---
        # map_settings = stage_data.get("map_settings", {})
        # grid_size = map_settings.get("grid_size", {})
        # grid_width  = grid_size.get("width")
        # grid_height = grid_size.get("height")
        # if not grid_width or not grid_height:
        #     raise ValueError("map_settings.grid_size の width / height が定義されていません。")

        # # --- 割合で指定された線分の始点と終点 ---
        # line_segment = epicenter_config.get("line_segment")
        # if not line_segment or "start" not in line_segment or "end" not in line_segment:
        #     raise ValueError("epicenter_distribution に line_segment の start/end が定義されていません。")

        # start_ratio = np.array(line_segment["start"], dtype=float)  # (y_ratio, x_ratio)
        # end_ratio   = np.array(line_segment["end"], dtype=float)

        # # --- 割合をグリッド座標に変換 ---
        # start_grid = start_ratio * np.array([grid_height, grid_width])
        # end_grid   = end_ratio   * np.array([grid_height, grid_width])

        # --- 共分散（なければデフォルト値） ---
        cov_along = stage_data[0].get("covariance_along_line", 1.0)
        cov_perp  = stage_data[0].get("covariance_perpendicular", 0.1)

        # --- 線分ベクトルと直交ベクトル ---
        line_vec = line[1] - line[0]
        line_length = np.linalg.norm(line_vec)
        line_dir = line_vec / line_length
        perp_dir = np.array([-line_dir[1], line_dir[0]])  # 線分に直交する方向

        # --- サンプリング ---
        t_along = np.clip(np.random.normal(loc=0.5, scale=np.sqrt(cov_along)), 0.0, 1.0)
        t_perp  = np.random.normal(loc=0.0, scale=np.sqrt(cov_perp))

        # --- 震源座標（グリッド番号）を計算 ---
        point_on_line = line[0] + t_along * line_vec
        offset = t_perp * perp_dir
        sampled_point = point_on_line + offset

        # --- 整数のグリッド番号に変換 ---
        grid_y = int(round(sampled_point[0]))
        grid_x = int(round(sampled_point[1]))

        # 範囲外クリップ
        grid_y = max(0, min(stage_data[2] - 1, grid_y))
        grid_x = max(0, min(stage_data[1] - 1, grid_x))

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

    get_stage = DefineEpicenter.get_stage_data(stage_data)
    line = DefineEpicenter.calcrate_line(get_stage)
    area = DefineEpicenter.calcrate_area(get_stage)
    epicenter = DefineEpicenter.define_epicenter(line, get_stage)

    print("sample_point_1 " + str(area[0]))
    print("sample_point_1_x " + str(area[0][0]))
    print("sample_point_1_y " + str(area[0][1]))
    print("sample_point_2 " + str(area[1]))
    print("sample_point_3 " + str(area[2]))
    print("sample_point_4 " + str(area[3]))

    print("震源位置（grid_y, grid_x）:", epicenter)
    # 例: 震源位置（grid_y, grid_x）: (29, 32)