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


