import json
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import platform

# 日本語フォントを設定
def setup_japanese_font():
    """日本語フォントを設定する関数"""
    if platform.system() == 'Windows':
        # Windowsの場合
        font_paths = [
            'C:/Windows/Fonts/msgothic.ttc',
            'C:/Windows/Fonts/yu Gothic.ttc',
            'C:/Windows/Fonts/meiryo.ttc'
        ]
    elif platform.system() == 'Darwin':  # macOS
        # Macの場合
        font_paths = [
            '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
            '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc',
            '/System/Library/Fonts/ヒラギノ明朝 W3.ttc',
            '/System/Library/Fonts/Yu Gothic.ttc'
        ]
    else:  # Linux
        # Linuxの場合
        font_paths = [
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/takao/TakaoGothic.ttf',
            '/usr/share/fonts/truetype/vlgothic/VLGothic-Regular.ttf'
        ]
    
    # 利用可能なフォントを探す
    font_prop = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = font_prop.get_name()
                print(f"日本語フォントを設定しました: {font_path}")
                break
            except:
                continue
    
    # フォントが見つからない場合は、システムフォントを試す
    if font_prop is None:
        system_fonts = {
            'Windows': ['MS Gothic', 'Yu Gothic', 'Meiryo'],
            'Darwin': ['Hiragino Kaku Gothic ProN', 'Hiragino Sans', 'Yu Gothic'],
            'Linux': ['Noto Sans CJK JP', 'Takao', 'VL Gothic']
        }
        
        os_name = platform.system()
        if os_name in system_fonts:
            for font_name in system_fonts[os_name]:
                try:
                    plt.rcParams['font.family'] = font_name
                    print(f"システムフォントを設定しました: {font_name}")
                    break
                except:
                    continue
    
    # それでも設定できない場合は、デフォルトフォントを使用
    if 'font.family' not in plt.rcParams or plt.rcParams['font.family'] == 'DejaVu Sans':
        print("警告: 日本語フォントが見つかりません。文字化けする可能性があります。")
        # 英語表記に変更
        return False
    
    return True

# 日本語フォントを設定
japanese_available = setup_japanese_font()

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
            "start": [20, 30],  #震源位置端1（マス座標：縦、横）
            "end": [40, 70]    #震源位置端2（マス座標：縦、横）
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
            "area": [[0, 30], [0, 100]],  # [[縦マス範囲], [横マス範囲]]
            "weakness": 0.9,  # 地盤の弱さ（0-1）
            "disaster_risk": "津波",  # 想定される災害
            "ground_type": "軟弱地盤"  # 地盤の種類
        },
        {
            "type": "川",
            "area": [[30, 50], [0, 100]],
            "weakness": 0.7,
            "disaster_risk": "氾濫",
            "ground_type": "軟弱地盤"
        },        
        {
            "type": "平地",
            "area": [[30, 50], [0, 100]],
            "weakness": 0.7,
            "disaster_risk": "火災",
            "ground_type": "沖積層"
        },
        {
            "type": "埋立地",
            "area": [[30, 50], [0, 100]],
            "weakness": 0.7,
            "disaster_risk": "液状化",
            "ground_type": "沖積層"
        },
        {
            "type": "三角州",
            "area": [[30, 50], [0, 100]],
            "weakness": 0.7,
            "disaster_risk": "液状化",
            "ground_type": "沖積層"
        },       
        {
            "type": "台地",
            "area": [[30, 50], [0, 100]],
            "weakness": 0.7,
            "disaster_risk": "地割れ",
            "ground_type": "沖積層"
        },
        {
            "type": "山地",
            "area": [[50, 100], [0, 100]],
            "weakness": 0.5,
            "disaster_risk": "土砂災害",
            "ground_type": "岩盤"
        }
    ]
}

def plot_map(config):
    """マップの地形と震源分布を視覚化する関数"""
    plt.figure(figsize=(15, 12))
    
    # 日本語フォントの設定を確認
    if japanese_available:
        title = "地震シミュレーション用マップ\n震源分布: 線分 + 2軸分散モデル"
        xlabel = "横マス数"
        ylabel = "縦マス数"
        line_label = "震源分布線分"
        spread_label = "震源分布の広がり"
    else:
        title = "Earthquake Simulation Map\nEpicenter Distribution: Line Segment + 2D Variance Model"
        xlabel = "Horizontal Grid"
        ylabel = "Vertical Grid"
        line_label = "Epicenter Distribution Line"
        spread_label = "Epicenter Distribution Spread"
    
    plt.title(title, fontsize=16, pad=20)
    
    # マス座標の範囲を設定
    grid_width = config['map_settings']['grid_size']['width']
    grid_height = config['map_settings']['grid_size']['height']
    plt.xlim(0, grid_width)
    plt.ylim(0, grid_height)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    # メッシュグリッドを表示
    plt.grid(True, alpha=0.3, linewidth=0.5)
    
    # 主要なグリッド線（10マスごと）を太く表示
    for i in range(0, grid_width + 1, 1):
        plt.axvline(x=i, color='gray', alpha=0.5, linewidth=1)
    for i in range(0, grid_height + 1, 1):
        plt.axhline(y=i, color='gray', alpha=0.5, linewidth=1)
    
    # マス番号を表示（10マスごと）
    for i in range(0, grid_width + 1, 10):
        plt.text(i, -2, str(i), ha='center', va='top', fontsize=8, alpha=0.7)
    for i in range(0, grid_height + 1, 10):
        plt.text(-2, i, str(i), ha='right', va='center', fontsize=8, alpha=0.7)
    
    # 地形の色マッピング
    terrain_colors = {
        "海": "blue",
        "川": "cyan", 
        "平地": "yellow",
        "埋立地": "orange",
        "三角州": "lightgreen",
        "台地": "brown",
        "山地": "green"
    }
    
    # 地形を描画
    for terrain in config['terrain']:
        area = terrain["area"]
        terrain_type = terrain["type"]
        color = terrain_colors.get(terrain_type, "gray")
        
        # ラベルを日本語または英語で設定
        if japanese_available:
            label = f"{terrain_type} ({terrain['disaster_risk']})"
        else:
            # 地形タイプを英語に変換
            terrain_english = {
                "海": "Sea", "川": "River", "平地": "Plain", 
                "埋立地": "Reclaimed Land", "三角州": "Delta", 
                "台地": "Plateau", "山地": "Mountain"
            }
            disaster_english = {
                "津波": "Tsunami", "氾濫": "Flood", "火災": "Fire",
                "液状化": "Liquefaction", "地割れ": "Ground Crack",
                "土砂災害": "Landslide"
            }
            terrain_en = terrain_english.get(terrain_type, terrain_type)
            disaster_en = disaster_english.get(terrain['disaster_risk'], terrain['disaster_risk'])
            label = f"{terrain_en} ({disaster_en})"
        
        # 地形エリアを塗りつぶし（マス座標）
        plt.fill_betweenx(
            [area[0][0], area[0][1]], area[1][0], area[1][1],
            color=color, alpha=0.6, 
            label=label
        )
    
    # 震源分布の線分を描画（マス座標）
    line_segment = config['epicenter_distribution']['line_segment']
    start = line_segment['start']  # [縦マス, 横マス]
    end = line_segment['end']      # [縦マス, 横マス]
    
    # 線分を太い赤線で描画（横マス, 縦マスの順でプロット）
    plt.plot([start[1], end[1]], [start[0], end[0]], 
             color='red', linewidth=4, label=line_label)
    
    # 線分の端点をマーカーで表示
    plt.scatter([start[1], end[1]], [start[0], end[0]], 
               color='red', s=100, marker='o', zorder=5)
    
    # 線分の端点に座標を表示
    plt.annotate(f'({start[1]},{start[0]})', 
                xy=(start[1], start[0]), xytext=(5, 5),
                textcoords='offset points', fontsize=8, color='red')
    plt.annotate(f'({end[1]},{end[0]})', 
                xy=(end[1], end[0]), xytext=(5, 5),
                textcoords='offset points', fontsize=8, color='red')
    
    # 震源分布の広がりを楕円で表示
    # 線分の中心点
    center_y = (start[0] + end[0]) / 2  # 縦マス
    center_x = (start[1] + end[1]) / 2  # 横マス
    
    # 線分の方向ベクトル
    vec = np.array([end[0] - start[0], end[1] - start[1]])  # [縦方向, 横方向]
    vec_norm = vec / np.linalg.norm(vec)
    perp = np.array([-vec_norm[1], vec_norm[0]])
    
    # 分散パラメータ
    sigma_along = config['epicenter_distribution']['covariance_along_line']
    sigma_perp = config['epicenter_distribution']['covariance_perpendicular']
    
    # 楕円の軸を計算（標準偏差の2倍）
    major_axis = 2 * np.sqrt(sigma_along)
    minor_axis = 2 * np.sqrt(sigma_perp)
    
    # 楕円を描画
    from matplotlib.patches import Ellipse
    angle = np.degrees(np.arctan2(vec_norm[1], vec_norm[0]))
    ellipse = Ellipse((center_x, center_y), 
                     major_axis, minor_axis, 
                     angle=angle, 
                     color='red', alpha=0.3, 
                     label=spread_label)
    plt.gca().add_patch(ellipse)
    
    # 凡例を表示
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    
    # アスペクト比を調整
    plt.gca().set_aspect('equal')
    
    # 軸の範囲を少し拡張してマス番号が見えるようにする
    plt.xlim(-5, grid_width + 5)
    plt.ylim(-5, grid_height + 5)
    
    plt.tight_layout()
    plt.show()

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

def normalize_area(area, grid_height, grid_width):
    # area: [[縦min, 縦max], [横min, 横max]]
    return [
        [area[0][0] / grid_height, area[0][1] / grid_height],
        [area[1][0] / grid_width, area[1][1] / grid_width]
    ]

def normalize_point(point, grid_height, grid_width):
    # point: [縦, 横]
    return [point[0] / grid_height, point[1] / grid_width]


def generate_config(stage_num = 1):
    """config.jsonを生成する関数"""
    config_path = os.path.join(os.path.dirname(__file__), f'map_sample{stage_num}_config.json')
    grid_height = DEFAULT_CONFIG['map_settings']['grid_size']['height']
    grid_width = DEFAULT_CONFIG['map_settings']['grid_size']['width']

    # 設定を整形
    formatted_config = {}
    for key, value in DEFAULT_CONFIG.items():
        if key == "terrain":
            # 地形情報を正規化して出力
            formatted_config[key] = []
            for t in value:
                t_copy = t.copy()
                t_copy['area'] = normalize_area(t['area'], grid_height, grid_width)
                formatted_config[key].append(format_terrain(t_copy))
        elif key == "epicenter_distribution":
            epi = value.copy()
            epi['line_segment'] = {
                'start': normalize_point(value['line_segment']['start'], grid_height, grid_width),
                'end': normalize_point(value['line_segment']['end'], grid_height, grid_width)
            }
            # 他の値はそのまま
            epi['covariance_along_line'] = value['covariance_along_line']
            epi['covariance_perpendicular'] = value['covariance_perpendicular']
            epi['depth_range'] = value['depth_range']
            formatted_config[key] = epi
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
    print(f"   - 線分始点: 縦マス {DEFAULT_CONFIG['epicenter_distribution']['line_segment']['start'][0]}, 横マス {DEFAULT_CONFIG['epicenter_distribution']['line_segment']['start'][1]}")
    print(f"   - 線分終点: 縦マス {DEFAULT_CONFIG['epicenter_distribution']['line_segment']['end'][0]}, 横マス {DEFAULT_CONFIG['epicenter_distribution']['line_segment']['end'][1]}")
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
        print(f"     * 範囲: 縦マス {terrain['area'][0]}, 横マス {terrain['area'][1]}")
        print(f"     * 地盤の弱さ: {terrain['weakness']}")
        print(f"     * 想定災害: {terrain['disaster_risk']}")
        print(f"     * 地盤の種類: {terrain['ground_type']}")
    
    # マップを視覚化
    #print(f"\nマップを視覚化しています...")
    #plot_map(DEFAULT_CONFIG)

if __name__ == "__main__":
    stage_num = 2  # ステージ番号を指定
    generate_config(stage_num) 