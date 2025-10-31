import json
import math

def calculate_total_score(buildings):
    """
    各建物のスコアを集計し、倒壊していない建物数に応じてボーナスを加える。

    :param buildings: [{"building_type": int, "building_strength": float, "score": int}, ...]
    :return: 合計スコア（int）
    """
    total_score = 0
    safe_buildings = 0

    for building in buildings:
        base_score = building["score"]
        strength = building["building_strength"]

        if strength == -1:
            # 倒壊：スコア1/2
            adjusted_score = base_score / 2
        else:
            # 無事：スコアそのまま＋カウント
            adjusted_score = base_score
            safe_buildings += 1

        total_score += adjusted_score

    # ボーナス係数を計算（例: 3棟生存 → ×1.3）
    bonus_multiplier = 1 + math.log(1 + safe_buildings) / 5

    final_score = int(total_score * bonus_multiplier)

    return final_score

def calc_building_stats(pane_result, building_config_path):
    # 建物設定の読み込み
    with open(building_config_path, "r", encoding="utf-8") as f:
        building_config = json.load(f)

    # 建物タイプ数を取得
    # type_indices = [int(k) for k in building_config.keys()]
    # max_type = max(type_indices)
    # num_types = max_type + 1
    num_types = len(building_config)

    # 建物種類ごとの倒壊数・スコア初期化（リストで管理）
    collapse_count = [0 for _ in range(num_types+1)]
    survive_count = [0 for _ in range(num_types+1)]

    # スコア計算用リスト
    buildings = []

    for x in range(len(pane_result)):
        for y in range(len(pane_result[x])):
            panel = pane_result[x][y]
            building_id = panel.building_type
            building_strength = panel.building_strength

            if building_id == -1: # 建物がないパネルはスキップ
                continue
            else:
                if building_strength == -1: # 倒壊している場合
                    collapse_count[building_id] += 1
                else: # 生存している場合
                    survive_count[building_id] += 1
            # print(f"Building ID: {building_id}, Strength: {building_strength}")

            # スコア計算用に情報を追加
            if building_id > 0:
                buildings.append({
                    "score": building_config[str(building_id -1)]["score"],
                    "building_strength": building_strength
                })

    # スコア計算
    total_score = calculate_total_score(buildings)

    # 建物種類ごとに結果を表示
    # for k in building_config.keys():
    #     idx = int(k)
    #     name = building_config[k]["name"]
    #     print(f"{name}（type={idx}）: 倒壊数={collapse_count[idx]} , 生存数={survive_count[idx]}")

    # print(f"合計スコア: {total_score}")

    # collapse_count, survive_countをリストで返す
    # return collapse_count, survive_count, total_score
    return sum(collapse_count), sum(survive_count), total_score

