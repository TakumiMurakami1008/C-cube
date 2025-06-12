import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import platform
from scipy.stats import multivariate_normal, truncnorm
import json
import os

# デフォルト設定
DEFAULT_CONFIG = {
    "map_settings": {
        "latitude_range": [30, 45],
        "longitude_range": [130, 145]
    },
    "epicenter_distribution": {
        "mean": [32.0, 138.0],
        "covariance": [[2.0, 0.0], [0.0, 2.0]]
    },
    "magnitude_distribution": {
        "min": 6.0,
        "max": 9.0,
        "mean": 7.5,
        "std": 0.8
    },
    "intensity_distribution": {
        "min": 1,
        "max": 7,
        "mean": 4,
        "std": 1.5
    },
    "terrain": [
        {
            "type": "海",
            "area": [[30, 35], [130, 145]],
            "weakness": 0.9,
            "disaster_risk": "津波"
        },
        {
            "type": "平地",
            "area": [[35, 40], [130, 145]],
            "weakness": 0.7,
            "disaster_risk": "液状化"
        },
        {
            "type": "山",
            "area": [[40, 45], [130, 145]],
            "weakness": 0.5,
            "disaster_risk": "土砂災害"
        }
    ]
}

def load_config():
    """config.jsonを読み込む関数"""
    config_path = os.path.join(os.path.dirname(__file__), 'map_sample1_config.json')
    
    if not os.path.exists(config_path):
        print("エラー: map_sample1_config.jsonが見つかりません。")
        print("generate_config.pyを実行してmap_sample1_config.jsonを生成してください。")
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    # 文字列として保存された配列を数値配列に変換
    def parse_array_str(array_str):
        """文字列として保存された配列を数値配列に変換"""
        # 文字列から余分な空白を削除
        array_str = array_str.replace(' ', '')
        # 文字列を評価して配列に変換
        try:
            return eval(array_str)
        except:
            return array_str
    
    # マップ設定の変換
    config['map_settings']['latitude_range'] = parse_array_str(config['map_settings']['latitude_range'])
    config['map_settings']['longitude_range'] = parse_array_str(config['map_settings']['longitude_range'])
    
    # 震源分布の変換
    config['epicenter_distribution']['mean'] = parse_array_str(config['epicenter_distribution']['mean'])
    config['epicenter_distribution']['covariance'] = parse_array_str(config['epicenter_distribution']['covariance'])
    config['epicenter_distribution']['depth_range'] = parse_array_str(config['epicenter_distribution']['depth_range'])
    
    # 地形情報の変換
    for terrain in config['terrain']:
        terrain['area'] = parse_array_str(terrain['area'])
    
    return config

# 日本語フォントを設定
if platform.system() == 'Windows':
    # Windowsの場合、MS Gothicを使用
    plt.rcParams['font.family'] = 'MS Gothic'
else:
    # Macの場合、標準フォント「ヒラギノ角ゴ」を使用
    font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()

def generate_magnitude(config):
    """マグニチュードを生成"""
    mag_config = config['magnitude_distribution']
    a = (mag_config['min'] - mag_config['mean']) / mag_config['std']
    b = (mag_config['max'] - mag_config['mean']) / mag_config['std']
    return truncnorm.rvs(a, b, loc=mag_config['mean'], scale=mag_config['std'])

def generate_intensity(config):
    """震度を生成"""
    int_config = config['intensity_distribution']
    a = (int_config['min'] - int_config['mean']) / int_config['std']
    b = (int_config['max'] - int_config['mean']) / int_config['std']
    return round(truncnorm.rvs(a, b, loc=int_config['mean'], scale=int_config['std']), 1)

def plot_probability_distribution(config):
    """震源地の確率分布をプロット"""
    mean = np.array(config['epicenter_distribution']['mean'])
    cov = np.array(config['epicenter_distribution']['covariance'])
    
    # グリッドを作成
    lat_grid = np.linspace(config['map_settings']['latitude_range'][0], 
                          config['map_settings']['latitude_range'][1], 
                          config['map_settings']['grid_size']['height'])
    lon_grid = np.linspace(config['map_settings']['longitude_range'][0], 
                          config['map_settings']['longitude_range'][1], 
                          config['map_settings']['grid_size']['width'])
    lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)
    
    # 確率分布を計算
    rv = multivariate_normal(mean, cov)
    pos = np.dstack((lat_mesh, lon_mesh))
    probabilities = rv.pdf(pos)
    
    # 確率分布をプロット
    plt.figure(figsize=(10, 8))
    plt.contourf(lon_mesh, lat_mesh, probabilities, levels=20, cmap='YlOrRd')
    plt.colorbar(label='確率密度')
    plt.title('震源地の確率分布')
    plt.xlabel('経度')
    plt.ylabel('緯度')
    plt.grid(True)
    plt.show()

def get_user_input_houses(config):
    """ユーザーから家の位置と壊れやすさを入力"""
    houses = []
    print("\n家の位置と壊れやすさを入力してください。")
    print("入力を終了するには、緯度に -1 を入力してください。")
    
    lat_range = config['map_settings']['latitude_range']
    lon_range = config['map_settings']['longitude_range']
    
    while True:
        try:
            lat = float(input(f"\n緯度 ({lat_range[0]}-{lat_range[1]}): "))
            if lat == -1:
                break
            if not (lat_range[0] <= lat <= lat_range[1]):
                print(f"緯度は{lat_range[0]}から{lat_range[1]}の間で入力してください。")
                continue
                
            lon = float(input(f"経度 ({lon_range[0]}-{lon_range[1]}): "))
            if not (lon_range[0] <= lon <= lon_range[1]):
                print(f"経度は{lon_range[0]}から{lon_range[1]}の間で入力してください。")
                continue
                
            fragility = float(input("壊れやすさ (0.0-1.0): "))
            if not (0 <= fragility <= 1):
                print("壊れやすさは0.0から1.0の間で入力してください。")
                continue
            
            houses.append({
                "coords": [lat, lon],
                "fragility": fragility
            })
            print(f"家を追加しました。現在の家の数: {len(houses)}")
            
        except ValueError:
            print("数値を入力してください。")
    
    return houses

def generate_epicenter(config):
    """確率分布に基づいて震源地を生成"""
    mean = np.array(config['epicenter_distribution']['mean'])
    cov = np.array(config['epicenter_distribution']['covariance'])
    
    # 2次元正規分布から直接サンプリング
    rv = multivariate_normal(mean, cov)
    lat, lon = rv.rvs()
    
    # 範囲内に収まるように調整
    lat = np.clip(lat, config['map_settings']['latitude_range'][0], 
                  config['map_settings']['latitude_range'][1])
    lon = np.clip(lon, config['map_settings']['longitude_range'][0], 
                  config['map_settings']['longitude_range'][1])
    
    # 震源の深さをランダムに生成
    depth = np.random.uniform(config['epicenter_distribution']['depth_range'][0],
                            config['epicenter_distribution']['depth_range'][1])
    
    return lat, lon, depth

def calculate_damage_probability(distance, magnitude, fragility, terrain_weakness):
    """震源地からの距離、マグニチュード、壊れやすさ、地形の弱さに基づいて被害確率を計算"""
    # 距離による減衰
    distance_factor = np.exp(-distance / (magnitude * 10))
    # マグニチュードによる影響
    magnitude_factor = magnitude / 9.0
    # 地形の弱さによる影響
    terrain_factor = terrain_weakness
    # 最終的な被害確率を計算
    return min(1.0, fragility * magnitude_factor * distance_factor * terrain_factor)

def determine_damage_status(damage_prob, intensity):
    """被害確率と震度から倒壊判定を行う"""
    # 震度による補正
    intensity_factor = intensity / 7.0
    # 最終的な倒壊確率を計算
    final_prob = damage_prob * intensity_factor
    
    if final_prob >= 0.8:
        return "完全倒壊"
    elif final_prob >= 0.6:
        return "大規模倒壊"
    elif final_prob >= 0.4:
        return "部分倒壊"
    elif final_prob >= 0.2:
        return "軽微な損傷"
    else:
        return "無被害"

def get_terrain_weakness(lat, lon, config):
    """指定された位置の地形の弱さを取得"""
    for terrain in config['terrain']:
        area = terrain['area']
        if (area[0][0] <= lat <= area[0][1] and 
            area[1][0] <= lon <= area[1][1]):
            return terrain['weakness']
    return 0.7  # デフォルト値

def plot_simulation(epicenter, houses, magnitude, intensity, config):
    """地震シミュレーション結果をプロット"""
    plt.figure(figsize=(12, 10))
    plt.title(f"地震シミュレーションマップ\nマグニチュード: {magnitude:.1f}, 最大震度: {intensity}")
    
    # 地図の背景を描画
    plt.xlim(config['map_settings']['longitude_range'])
    plt.ylim(config['map_settings']['latitude_range'])
    plt.xlabel("経度")
    plt.ylabel("緯度")
    
    # 地形を描画
    for t in config['terrain']:
        area = t["area"]
        if t["type"] == "海":
            color = "blue"
        elif t["type"] == "山":
            color = "green"
        elif t["type"] == "平地":
            color = "yellow"
        plt.fill_betweenx(
            [area[0][0], area[0][1]], area[1][0], area[1][1],
            color=color, alpha=0.3, label=f"{t['type']} ({t['disaster_risk']})"
        )
    
    # 震源地をプロット
    plt.scatter(epicenter[1], epicenter[0], color='red', label="震源地", s=300, marker='*')
    
    # 地震影響範囲を描画
    base_radius = magnitude * 0.5
    plt.gca().set_aspect('equal')
    circle = plt.Circle((epicenter[1], epicenter[0]), base_radius,
                       color='purple', alpha=0.2, label="地震影響範囲")
    plt.gca().add_artist(circle)
    
    # 家をプロット（被害確率に基づく色分け）
    print("\n=== 地震による家の被害状況 ===")
    for i, house in enumerate(houses, 1):
        coords = house["coords"]
        fragility = house["fragility"]
        
        # 震源地からの距離を計算
        distance = np.sqrt((coords[0] - epicenter[0])**2 + (coords[1] - epicenter[1])**2)
        # 地形の弱さを取得
        terrain_weakness = get_terrain_weakness(coords[0], coords[1], config)
        # 被害確率を計算
        damage_prob = calculate_damage_probability(distance, magnitude, fragility, terrain_weakness)
        # 倒壊判定
        damage_status = determine_damage_status(damage_prob, intensity)
        
        # 被害状況を表示
        print(f"\n家 {i}:")
        print(f"位置: 緯度 {coords[0]:.2f}, 経度 {coords[1]:.2f}")
        print(f"震源地からの距離: {distance:.2f}度")
        print(f"壊れやすさ: {fragility:.2f}")
        print(f"地形の弱さ: {terrain_weakness:.2f}")
        print(f"被害確率: {damage_prob:.2f}")
        print(f"判定結果: {damage_status}")
        
        # 被害確率に基づいて色を設定
        if damage_prob >= 0.8:
            color = 'darkred'
        elif damage_prob >= 0.6:
            color = 'red'
        elif damage_prob >= 0.4:
            color = 'orange'
        elif damage_prob >= 0.2:
            color = 'yellow'
        else:
            color = 'green'
            
        plt.scatter(coords[1], coords[0], color=color, 
                   label=f"家 {i} ({damage_status})", s=50)
    
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    # 設定を読み込む
    config = load_config()
    if config is None:
        return
    
    # 震源地の確率分布を表示
    print("震源地の確率分布を表示します...")
    plot_probability_distribution(config)
    
    # ユーザーから家の情報を入力
    houses = get_user_input_houses(config)
    
    if not houses:
        print("家の情報が入力されませんでした。プログラムを終了します。")
        return
    
    # 震源地を生成
    epicenter = generate_epicenter(config)
    print(f"\n震源地が生成されました:")
    print(f"緯度: {epicenter[0]:.2f}")
    print(f"経度: {epicenter[1]:.2f}")
    print(f"深さ: {epicenter[2]:.2f} km")
    
    # マグニチュードと震度を生成
    magnitude = generate_magnitude(config)
    intensity = generate_intensity(config)
    print(f"マグニチュード: {magnitude:.1f}")
    print(f"最大震度: {intensity}")
    
    # シミュレーション結果を表示
    print("\n地震シミュレーションを実行します...")
    plot_simulation(epicenter, houses, magnitude, intensity, config)

if __name__ == "__main__":
    main()