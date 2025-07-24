import json
from calcurate_score import calculate_total_score

def calc_building_stats(pane_result, building_config_path):
    # 建物設定の読み込み
    with open(building_config_path, "r", encoding="utf-8") as f:
        building_config = json.load(f)

    # 建物タイプ数を取得
    type_indices = [int(k) for k in building_config.keys()]
    max_type = max(type_indices)
    num_types = max_type + 1

    # 建物種類ごとの倒壊数・スコア初期化（リストで管理）
    collapse_count = [0 for _ in range(num_types)]
    survive_count = [0 for _ in range(num_types)]

    # スコア計算用リスト
    buildings = []

    for i in range(len(pane_result)):
        for j in range(len(pane_result[i])):
            panel = pane_result[i][j]
            building_type = panel[0]
            building_strength = panel[1]
            # 建物がないパネルはスキップ
            if building_type == 0:
                continue
            if building_strength == -1:
                collapse_count[building_type] += 1
            else:
                survive_count[building_type] += 1

            # スコア計算用に情報を追加
            buildings.append({
                "score": building_config[str(building_type)]["score"],
                "building_strength": building_strength
            })

    # スコア計算
    total_score = calculate_total_score(buildings)

    # 建物種類ごとに結果を表示
    for k in building_config.keys():
        idx = int(k)
        name = building_config[k]["name"]
        print(f"{name}（type={idx}）: 倒壊数={collapse_count[idx]} , 生存数={survive_count[idx]}")

    print(f"合計スコア: {total_score}")

    # collapse_count, survive_countをリストで返す
    return collapse_count, survive_count, total_score

