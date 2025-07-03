import json
import os

# デフォルト設定
DEFAULT_CONFIG = {
    "map_settings": {
        "grid_size": {
            "width": 100,  # 経度方向のマス数
            "height": 100  # 緯度方向のマス数
        },
        "latitude_range": [30, 45],  # 緯度の範囲
        "longitude_range": [130, 145]  # 経度の範囲
    },
    "epicenter_distribution": {
        "line_segment": {
            "start": [32.0, 135.0],  #震源位置端1（緯度、経度）
            "end": [34.0, 140.0]    #震源位置端2（緯度、経度）
        },
        "covariance_along_line": 1.0,  #地震並行方向の広がり
        "covariance_perpendicular": 0.5,  #地震垂直方向の広がり
        "depth_range": [0, 100]  #震源の深さ範囲（km）
    },
    "magnitude_distribution": {
        "min": 6.0,  # 最小マグニチュード
        "max": 9.0,  # 最大マグニチュード
        "mean": 7.5,  # 平均マグニチュード
        "std": 0.8   # 標準偏差
    },
    "intensity_distribution": {
        "min": 1,    # 最小震度
        "max": 7,    # 最大震度
        "mean": 4,   # 平均震度
        "std": 1.5   # 標準偏差
    },
    "terrain": [
        {
            "type": "海",
            "area": [[30, 35], [130, 145]],  # [[緯度範囲], [経度範囲]]
            "weakness": 0.9,  # 地盤の弱さ（0-1）
            "disaster_risk": "津波",  # 想定される災害
            "ground_type": "軟弱地盤"  # 地盤の種類
        },
        {
            "type": "川",
            "area": [[35, 40], [130, 145]],
            "weakness": 0.7,
            "disaster_risk": "氾濫",
            "ground_type": ""
        },        
        {
            "type": "平地",
            "area": [[35, 40], [130, 145]],
            "weakness": 0.7,
            "disaster_risk": "火災",
            "ground_type": "沖積層"
        },
        {
            "type": "埋立地",
            "area": [[35, 40], [130, 145]],
            "weakness": 0.7,
            "disaster_risk": "液状化",
            "ground_type": "沖積層"
        },
        {
            "type": "三角州",
            "area": [[35, 40], [130, 145]],
            "weakness": 0.7,
            "disaster_risk": "液状化",
            "ground_type": "沖積層"
        },       
        {
            "type": "台地",
            "area": [[35, 40], [130, 145]],
            "weakness": 0.7,
            "disaster_risk": "地割れ",
            "ground_type": "沖積層"
        },
        {
            "type": "山地",
            "area": [[40, 45], [130, 145]],
            "weakness": 0.5,
            "disaster_risk": "土砂災害",
            "ground_type": "岩盤"
        }
    ]
}

def format_array(arr):
    """配列を一行で表示するためのフォーマット関数"""
    if isinstance(arr, (list, tuple)):
        if not arr:  # 空の配列
            return "[]"
        if all(not isinstance(item, (dict, list, tuple)) for item in arr):  # 単純な配列
            return "[" + ", ".join(str(item) for item in arr) + "]"
        # ネストされた配列の場合
        return "[" + ", ".join(format_array(item) for item in arr) + "]"
    return str(arr)

def format_terrain(terrain):
    """地形情報を一行で表示するためのフォーマット関数"""
    return {
        "type": terrain["type"],
        "area": format_array(terrain["area"]),
        "weakness": terrain["weakness"],
        "disaster_risk": terrain["disaster_risk"],
        "ground_type": terrain["ground_type"]
    }

def generate_config(stage_num = 1):
    """config.jsonを生成する関数"""
    config_path = os.path.join(os.path.dirname(__file__), f'map_sample{stage_num}_config.json')
    
    # 設定を整形
    formatted_config = {}
    for key, value in DEFAULT_CONFIG.items():
        if key == "terrain":
            # 地形情報を特別に処理
            formatted_config[key] = [format_terrain(t) for t in value]
        elif isinstance(value, dict):
            formatted_config[key] = {}
            for subkey, subvalue in value.items():
                if isinstance(subvalue, (list, tuple)):
                    formatted_config[key][subkey] = format_array(subvalue)
                else:
                    formatted_config[key][subkey] = subvalue
        elif isinstance(value, list):
            formatted_config[key] = format_array(value)
        else:
            formatted_config[key] = value
    
    # config.jsonを生成（既存のファイルは上書き）
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_config, f, ensure_ascii=False, indent=4, separators=(',', ': '))
    
    if os.path.exists(config_path):
        print(f"config.jsonを上書きしました: {config_path}")
    else:
        print(f"config.jsonを生成しました: {config_path}")
    
    print("\n生成された設定の概要:")
    print(f"1. マップ設定:")
    print(f"   - グリッドサイズ: {DEFAULT_CONFIG['map_settings']['grid_size']['width']}x{DEFAULT_CONFIG['map_settings']['grid_size']['height']}")
    print(f"   - 緯度範囲: {DEFAULT_CONFIG['map_settings']['latitude_range']}")
    print(f"   - 経度範囲: {DEFAULT_CONFIG['map_settings']['longitude_range']}")
    
    print(f"\n2. 震源分布:")
    print(f"   - 線分始点: 緯度 {DEFAULT_CONFIG['epicenter_distribution']['line_segment']['start'][0]}, 経度 {DEFAULT_CONFIG['epicenter_distribution']['line_segment']['start'][1]}")
    print(f"   - 線分終点: 緯度 {DEFAULT_CONFIG['epicenter_distribution']['line_segment']['end'][0]}, 経度 {DEFAULT_CONFIG['epicenter_distribution']['line_segment']['end'][1]}")
    print(f"   - 並行方向分散: {DEFAULT_CONFIG['epicenter_distribution']['covariance_along_line']}")
    print(f"   - 垂直方向分散: {DEFAULT_CONFIG['epicenter_distribution']['covariance_perpendicular']}")
    print(f"   - 深さ範囲: {DEFAULT_CONFIG['epicenter_distribution']['depth_range']} km")
    
    print(f"\n3. マグニチュード範囲:")
    print(f"   - 最小: {DEFAULT_CONFIG['magnitude_distribution']['min']}")
    print(f"   - 最大: {DEFAULT_CONFIG['magnitude_distribution']['max']}")
    
    print(f"\n4. 震度範囲:")
    print(f"   - 最小: {DEFAULT_CONFIG['intensity_distribution']['min']}")
    print(f"   - 最大: {DEFAULT_CONFIG['intensity_distribution']['max']}")
    
    print(f"\n5. 地形情報:")
    for terrain in DEFAULT_CONFIG['terrain']:
        print(f"   - {terrain['type']}:")
        print(f"     * 範囲: 緯度 {terrain['area'][0]}, 経度 {terrain['area'][1]}")
        print(f"     * 地盤の弱さ: {terrain['weakness']}")
        print(f"     * 想定災害: {terrain['disaster_risk']}")
        print(f"     * 地盤の種類: {terrain['ground_type']}")

if __name__ == "__main__":
    stage_num = 1  # ステージ番号を指定
    generate_config(stage_num) 