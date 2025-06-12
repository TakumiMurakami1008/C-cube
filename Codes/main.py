import pygame
from pygame.locals import *
import numpy as np
import sys
from pathlib import Path
import json
import os

from dataclasses import dataclass
from EQSimulator import EQSimulatorVariableRho
import PanelManager

@dataclass 
class Coordinate: #座標
    x: float
    y: float

@dataclass 
class Earthquake: #地震
    magnitude: float        # マグニチュード
    depth: float            # 深さ（km）
    epicenter: Coordinate   # 震源地（座標）

@dataclass
class Panel: #パネル
    # position: Coordinate     # パネルの座標（配列の場所で自動計算？）
    has_building: bool         # 建物の有無
    building_strength: float   # 建物がある場合、建物の強度（0~1）、-1の場合壊れている建物とする
    shaking: float             # 地震の揺れの大きさ（例：加速度や震度）
    ground_strength: float     # 地盤の強さ（0〜1などで表現）
    terrain_type: str          # 地形情報（例："hill", "plain", "coast", etc.）



def main():
    # pygame.init()                                   # Pygameの初期化
    # screen = pygame.display.set_mode((400, 300))    # 400 x 300の大きさの画面を作る
    # pygame.display.set_caption("Game")              # 画面上部に表示するタイトルを設定

    # データ読み込み
    # TODO

    # while (1): # メインループ
    # pygame.display.update()     # 画面を更新
    
    # シミュレータ起動
    # TODO

    """
    境界条件の都合で端っこの値は正しく使えないため、
    ・シミュレーションの範囲をより広げて計算？
    ・シミュレーションの範囲を大きく広げ震源を真ん中に設定してシミュ->シミュ後に座標を移動？
    いずれにせよ、シミュレーションした範囲すべてを使うことはできないことに留意
    """

    file_path = Path("../Config") / f"map_config.json"
    # with open(f"map_stage{stage_num}.json", "r") as f:
    with open(file_path, "r", encoding="utf-8_sig") as f:
        map_data = json.load(f)
        tile_width = map_data["tile_width"] 
        tile_height = map_data["tile_width"] 
    
    sim = EQSimulatorVariableRho(
            epicenter=(2, 5), #震源​
            magnitude=10, #地震の規模​
            grid_shape= (tile_width, tile_height),
            rho_map=np.ones((tile_width, tile_height)), #地盤密度を持つ配列​
            mu=1.0, #弾性係数​
            dt=0.05
        )
    max_disp = sim.run(steps=100) #揺れの大きの最大値を持つ配列​

    pane = PanelManager.PanelManager(
        stage_num= 0, 
        config_path = "../Config/map_config.json", # マップ共通のコンフィグを想定
        grid_shape=(tile_width, tile_height), 
        )

    pane.simulate(max_disp = max_disp)
    
    import matplotlib.pyplot as plt
    # プロット
    plt.imshow(max_disp, cmap='viridis', interpolation='nearest')
    plt.colorbar(label='Value')  # カラーバーを表示
    plt.title('2D Array Visualization')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.savefig("2d_array_visualization.png", dpi=300, bbox_inches='tight')  # 高解像度・余白調整付き
    # plt.savefig("2d_array_visualization.jpeg", dpi=300, bbox_inches='tight')
    plt.show()
    

    pane.showPanelState()


    # イベント処理
    # for event in pygame.event.get():
    #     if event.type == QUIT:  # 閉じるボタンが押されたら終了
    #         pygame.quit()       # Pygameの終了(画面閉じられる)
    #         sys.exit()


if __name__ == "__main__":
    main()
