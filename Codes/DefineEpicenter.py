import numpy as np

class DefineEpicenter:
    @staticmethod
    def define_epicenter(stage_data: dict) -> tuple:
        """
        ステージのJSONデータから震源を1点サンプリングして返す

        Args:
            stage_data (dict): JSONから読み込んだステージ設定データ

        Returns:
            (latitude, longitude)
        """

        # JSONからパラメータを抽出
        epicenter_config = stage_data.get("epicenter_distribution", {})

        # 線分の始点と終点
        line_segment = epicenter_config.get("line_segment")
        if not line_segment or "start" not in line_segment or "end" not in line_segment:
            raise ValueError("epicenter_distributionにline_segmentのstart/endが定義されていません。")

        start = np.array(line_segment["start"])
        end = np.array(line_segment["end"])

        # 共分散（なければデフォルト値）
        cov_along = epicenter_config.get("covariance_along_line", 1.0)
        cov_perp = epicenter_config.get("covariance_perpendicular", 0.1)

        # 線分ベクトルと直交ベクトル
        line_vec = end - start
        line_length = np.linalg.norm(line_vec)
        line_dir = line_vec / line_length
        perp_dir = np.array([-line_dir[1], line_dir[0]])  # 線分に直交する方向

        # サンプリング（0〜1の範囲中心、外れ値対策もあり）
        t_along = np.clip(np.random.normal(loc=0.5, scale=np.sqrt(cov_along)), 0.0, 1.0)
        t_perp = np.random.normal(loc=0.0, scale=np.sqrt(cov_perp))

        # 震源座標を計算
        point_on_line = start + t_along * line_vec
        offset = t_perp * perp_dir
        sampled_point = point_on_line + offset

        return tuple(sampled_point)

    

if __name__ == "__main__":
    # 例: 線分の始点と終点
    start = [32.0, 135.0]
    end = [34.0, 140.0]
    cov_along = 0.02       # 小さくすると線分の中心付近に集中
    cov_perp = 0.0001      # 線からほとんどずれない

    # start = epicenter_distribution.line_segment.start, # 震源発生中心（直線）の始点
    # end = epicenter_distribution.line_segment.end, # 震源発生中心（直線）の終点
    # cov_l = epicenter_distribution.covariance_along_line, # 震源の確率密度（線分に沿った方向）
    # cov_p = epicenter_distribution.covariance_perpendicular # 震源の確率密度（線分に直交する方向）

    epicenter = DefineEpicenter.define_epicenter({
        "epicenter_distribution": {
            "line_segment": {
                "start": start,
                "end": end
            },
            "covariance_along_line": cov_along,
            "covariance_perpendicular": cov_perp
        }
    })
    print("震源位置（緯度・経度）:", epicenter)