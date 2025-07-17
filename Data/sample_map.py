import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import platform
from scipy.stats import multivariate_normal, truncnorm
import json
import os

# 設定ファイルの読み込み
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 日本語フォントを設定
if platform.system() == 'Windows':
    # Windowsの場合、MS Gothicを使用
    plt.rcParams['font.family'] = 'MS Gothic'
else:
    # Macの場合、標準フォント「ヒラギノ角ゴ」を使用
    font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()

# 設定を読み込む
config = load_config()

# 地図の範囲を設定
latitude_range = tuple(config['map_settings']['latitude_range'])
longitude_range = tuple(config['map_settings']['longitude_range'])

def generate_magnitude():
    """マグニチュードを生成"""
    mag_config = config['magnitude_distribution']
    a = (mag_config['min'] - mag_config['mean']) / mag_config['std']
    b = (mag_config['max'] - mag_config['mean']) / mag_config['std']
    return truncnorm.rvs(a, b, loc=mag_config['mean'], scale=mag_config['std'])

def generate_intensity():
    """震度を生成"""
    int_config = config['intensity_distribution']
    a = (int_config['min'] - int_config['mean']) / int_config['std']
    b = (int_config['max'] - int_config['mean']) / int_config['std']
    return round(truncnorm.rvs(a, b, loc=int_config['mean'], scale=int_config['std']), 1)

def plot_probability_distribution():
    """震源地の確率分布をプロット"""
    mean = np.array(config['epicenter_distribution']['mean'])
    cov = np.array(config['epicenter_distribution']['covariance'])
    
    # グリッドを作成
    lat_grid = np.linspace(latitude_range[0], latitude_range[1], 100)
    lon_grid = np.linspace(longitude_range[0], longitude_range[1], 100)
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

def get_user_input_houses():
    """ユーザーから家の位置と壊れやすさを入力"""
    houses = []
    print("\n家の位置と壊れやすさを入力してください。")
    print("入力を終了するには、緯度に -1 を入力してください。")
    
    while True:
        try:
            lat = float(input("\n緯度 (30-45): "))
            if lat == -1:
                break
            if not (latitude_range[0] <= lat <= latitude_range[1]):
                print(f"緯度は{latitude_range[0]}から{latitude_range[1]}の間で入力してください。")
                continue
                
            lon = float(input("経度 (130-145): "))
            if not (longitude_range[0] <= lon <= longitude_range[1]):
                print(f"経度は{longitude_range[0]}から{longitude_range[1]}の間で入力してください。")
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

def generate_epicenter():
    """確率分布に基づいて震源地を生成"""
    mean = np.array(config['epicenter_distribution']['mean'])
    cov = np.array(config['epicenter_distribution']['covariance'])
    
    # 2次元正規分布から直接サンプリング
    rv = multivariate_normal(mean, cov)
    lat, lon = rv.rvs()
    
    # 範囲内に収まるように調整
    lat = np.clip(lat, latitude_range[0], latitude_range[1])
    lon = np.clip(lon, longitude_range[0], longitude_range[1])
    
    return lat, lon

def calculate_damage_probability(distance, magnitude, fragility):
    """震源地からの距離、マグニチュード、壊れやすさに基づいて被害確率を計算"""
    # 距離による減衰
    distance_factor = np.exp(-distance / (magnitude * 10))
    # マグニチュードによる影響
    magnitude_factor = magnitude / 9.0
    # 最終的な被害確率を計算
    return min(1.0, fragility * magnitude_factor * distance_factor)

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

def plot_simulation(epicenter, houses, magnitude, intensity):
    """地震シミュレーション結果をプロット"""
    terrain = config['terrain']
    
    plt.figure(figsize=(12, 10))
    plt.title(f"地震シミュレーションマップ\nマグニチュード: {magnitude:.1f}, 最大震度: {intensity}")
    
    # 地図の背景を描画
    plt.xlim(longitude_range)
    plt.ylim(latitude_range)
    plt.xlabel("経度")
    plt.ylabel("緯度")
    
    # 地形を描画
    for t in terrain:
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
    # マグニチュードに基づく基本の影響範囲（度単位）
    base_radius = magnitude * 0.5
    
    # 完全な円を描画するために、アスペクト比を1:1に設定
    plt.gca().set_aspect('equal')
    
    # 影響範囲を描画
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
        # 被害確率を計算
        damage_prob = calculate_damage_probability(distance, magnitude, fragility)
        # 倒壊判定
        damage_status = determine_damage_status(damage_prob, intensity)
        
        # 被害状況を表示
        print(f"\n家 {i}:")
        print(f"位置: 緯度 {coords[0]:.2f}, 経度 {coords[1]:.2f}")
        print(f"震源地からの距離: {distance:.2f}度")
        print(f"壊れやすさ: {fragility:.2f}")
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
    # 震源地の確率分布を表示
    print("震源地の確率分布を表示します...")
    plot_probability_distribution()
    
    # ユーザーから家の情報を入力
    houses = get_user_input_houses()
    
    if not houses:
        print("家の情報が入力されませんでした。プログラムを終了します。")
        return
    
    # 震源地を生成
    epicenter = generate_epicenter()
    print(f"\n震源地が生成されました: 緯度 {epicenter[0]:.2f}, 経度 {epicenter[1]:.2f}")
    
    # マグニチュードと震度を生成
    magnitude = generate_magnitude()
    intensity = generate_intensity()
    print(f"マグニチュード: {magnitude:.1f}")
    print(f"最大震度: {intensity}")
    
    # シミュレーション結果を表示
    print("\n地震シミュレーションを実行します...")
    plot_simulation(epicenter, houses, magnitude, intensity)

if __name__ == "__main__":
    main()