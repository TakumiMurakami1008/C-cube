import json

def load_building_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    building_settings = config.get("building_settings", {})
    
    # 各建物IDごとの max_count を取得して辞書にまとめる
    building_max_counts = {
        building_id: data.get("max_count", 0)
        for building_id, data in building_settings.items()
    }
    
    return building_max_counts

if __name__ == "__main__":
    # 設定ファイルのパスを指定
    config_path = "../Config/map_sample2_config.json"
    building_max_counts = load_building_config(config_path)

    # 例: ID の最大数を取得
    id = 0
    print(f"{id} の配置可能最大数:", building_max_counts.get(str(id), 0))