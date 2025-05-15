import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import platform

# 日本語フォントを設定
if platform.system() == 'Windows':
    # Windowsの場合、MS Gothicを使用
    plt.rcParams['font.family'] = 'MS Gothic'
else:
    # Macの場合、標準フォント「ヒラギノ角ゴ」を使用
    font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()

# 地図の範囲を設定 (緯度と経度)
latitude_range = (30, 45)  # 緯度
longitude_range = (130, 145)  # 経度

# 地震の震源地 (例: 緯度, 経度)
epicenter = (33, 139)  #震源地
magnitude = 8.5  # 地震の規模

# 家の情報 (座標と壊れやすさ)
houses = [
    {"coords": (35.1, 142), "fragility": 0}, # 壊れやすさ: 0.0 (壊れにくい) ～ 1.0 (壊れやすい)
    {"coords": (43, 143), "fragility": 0.2}, 
    {"coords": (37, 136), "fragility": 0.4},
    {"coords": (40.5, 140), "fragility": 0.6},
    {"coords": (35.5, 132), "fragility": 0.8},
    {"coords": (42, 138), "fragility": 1.0},
]

# 地形情報 (座標範囲と属性)
terrain = [
    {"type": "海", "area": [(30, 35), (130, 145)], "weakness": 0.9, "disaster_risk": "津波"},
    {"type": "平地", "area": [(35, 40), (130, 145)], "weakness": 0.7, "disaster_risk": "液状化"},
    {"type": "山", "area": [(40, 45), (130, 145)], "weakness": 0.5, "disaster_risk": "土砂災害"},
]

# 地図を描画
plt.figure(figsize=(8, 8))
plt.title("地震シミュレーションマップ")

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
        [area[0][0], area[0][1]], area[1][0], area[1][1], color=color, alpha=0.3, label=f"{t['type']} ({t['disaster_risk']})"
    )

# 震源地をプロット
plt.scatter(epicenter[1], epicenter[0], color='red', label="震源地", s=300, marker='*')

# 影響範囲を描画 (単純な円で表現)
radius = magnitude  # 地震の規模を影響範囲に反映
circle = plt.Circle((epicenter[1], epicenter[0]), radius, color='purple', alpha=0.3, label="地震影響範囲")
plt.gca().add_artist(circle)

# 家をプロット
for house in houses:
    coords = house["coords"]
    fragility = house["fragility"]
    # 壊れやすさに応じて6段階の色を設定
    if fragility >= 1.0:
        color = 'darkred'  # 最も壊れやすい
    elif fragility >= 0.8:
        color = 'red'  # 非常に壊れやすい
    elif fragility >= 0.6:
        color = 'orange'  # 壊れやすい
    elif fragility >= 0.4:
        color = 'yellow'  # 普通
    elif fragility >= 0.2:
        color = 'lightgreen'  # 壊れにくい
    else:
        color = 'green'  # 最も壊れにくい
    plt.scatter(coords[1], coords[0], color=color, label=f"家 (壊れやすさ: {fragility})", s=50)

# 凡例を追加
plt.legend()

# 地図を表示
plt.grid(True)
plt.show()