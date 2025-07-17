import numpy as np

def define_epicenter_on_ocean(
    start: list,  # [lat, lon]
    end: list,    # [lat, lon]
    covariance_along_line: float,
    covariance_perpendicular: float
) -> tuple:
    """プレート境界（海上）に沿った震源をサンプリングする"""
    start = np.array(start)
    end = np.array(end)

    # 線分のベクトル
    line_vec = end - start
    line_length = np.linalg.norm(line_vec)
    line_dir = line_vec / line_length

    # 線に直交するベクトル（2Dの回転）
    perp_dir = np.array([-line_dir[1], line_dir[0]])

    # サンプリング（線上、線直交方向）
    t_along = np.random.normal(loc=0.5, scale=np.sqrt(covariance_along_line))
    t_perp = np.random.normal(loc=0.0, scale=np.sqrt(covariance_perpendicular))

    # 線分上の位置 + 垂直方向のズレ
    point_on_line = start + t_along * line_vec
    offset = t_perp * perp_dir

    sampled_point = point_on_line + offset
    print(f"[海] Sampled epicenter: {sampled_point}")
    return tuple(sampled_point)

def define_epicenter_on_land(
    lat_range: tuple,
    lon_range: tuple
) -> tuple:
    """陸上の震源（完全ランダム）を仮に決定"""
    lat = np.random.uniform(*lat_range)
    lon = np.random.uniform(*lon_range)
    print(f"[陸] Sampled epicenter: ({lat}, {lon})")
    return (lat, lon)

def define_epicenter(
    ocean_prob: float,
    ocean_line_start: list,
    ocean_line_end: list,
    cov_along: float,
    cov_perp: float,
    land_lat_range: tuple,
    land_lon_range: tuple
) -> tuple:
    """全体の震源を定義（まず海か陸かを抽選）"""
    if np.random.rand() < ocean_prob:
        return define_epicenter_on_ocean(
            ocean_line_start, ocean_line_end, cov_along, cov_perp
        )
    else:
        return define_epicenter_on_land(land_lat_range, land_lon_range)

"""テスト用"""
if __name__ == "__main__":
    ocean_prob = 0.7
    ocean_line_start = [32.0, 135.0]
    ocean_line_end = [34.0, 140.0]
    cov_along = 0.02
    cov_perp = 0.0001
    land_lat_range = (33.0, 36.0)
    land_lon_range = (135.0, 138.0)

    for i in range(5):
        print(f"試行 {i+1}:")
        epicenter = define_epicenter(
            ocean_prob,
            ocean_line_start,
            ocean_line_end,
            cov_along,
            cov_perp,
            land_lat_range,
            land_lon_range
        )

        print("震源位置（緯度・経度）:", epicenter)