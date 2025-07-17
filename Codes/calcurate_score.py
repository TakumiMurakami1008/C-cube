def calculate_total_score(buildings):
    """
    各建物のスコアを集計し、無事な建物数に応じてボーナスをかける

    :param buildings: 各建物の情報リスト [{"score": int, "building_strength": float}, ...]
    :return: 総合スコア
    """
    total_score = 0
    safe_buildings = 0

    for building in buildings:
        base_score = building["score"]
        strength = building["building_strength"]

        if strength == -1:
            # 倒壊した場合はスコア1/2
            adjusted_score = base_score / 2
        else:
            # 無事ならスコアそのまま＋カウント
            adjusted_score = base_score
            safe_buildings += 1

        total_score += adjusted_score

    # 無事な建物数に応じてボーナス
    total_score *= safe_buildings

    return total_score

