import pygame
from pygame.locals import *
import numpy as np
import sys
from pathlib import Path
import json
import os

from dataclasses import dataclass
import DefineEpicenter
import DefineMagnitude
from DefineWeaknessMap import DefineWeaknessMap
from EQSimulator import EQSimulatorVariableRho
import PanelManager
import result_inf

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
    building_type: int         # 建物の種類（例 0: なし, 1: 家, 2: ビル, ...）
    building_strength: float   # 建物がある場合、建物の強度（0~1）、-1の場合壊れている建物とする
    shaking: float             # 受けた地震の揺れの大きさ（例：加速度や震度）
    waving: float              # 受けた津波の波の大きさ（例：波の高さ、勢い）
    ground_strength: float     # 地盤の強さ（0〜1などで表現）
    terrain_type: str          # 地形情報（例："hill", "plain", "coast", etc.）
    item_id: int             # パネルに設置されているアイテムのID（-1ならなし）

@dataclass
class Player: #プレイヤー
    score: int                 # スコア
    position: Coordinate       # 位置（座標）
    health: float              # 健康状態（0~1などで表現）



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
    with open(file_path, "r", encoding="utf-8_sig") as f:
        map_data = json.load(f)
        tile_width = map_data["tile_width"] 
        tile_height = map_data["tile_height"] 

    stage_num = 99 # ステージ番号 TODO:ステージ番号を選択画面から決定する


    with open(f"map_sample{stage_num}_config.json", "r") as f:
        stage_data = json.load(f)

    # 震源地を決める関数
    epicenter = DefineEpicenter.define_epicenter(
        stage_data = stage_data # ステージのコンフィグファイル
    )
    # マグニチュードを決める関数
    magnitude = DefineMagnitude.define_magnitude(
        stage_data = stage_data
    )

    weakness_map_creator = DefineWeaknessMap(
        stage_data = stage_data
    )
    weakness_map = weakness_map_creator.get_weakness_map()

    sim = EQSimulatorVariableRho(
            epicenter=epicenter, #震源​
            magnitude=magnitude, #地震の規模​
            grid_shape= (tile_width, tile_height),
            rho_map = weakness_map,
            # rho_map=np.ones((grid_width, grid_height)), #地盤密度を持つ配列​
            mu=10.0, #弾性係数​
            dt=0.05
        )
    max_disp = sim.run(steps=200) #揺れの大きの最大値を持つ配列​

    pane = PanelManager.PanelManager(
        map_data=map_data, # マップのコンフィグファイル
        stage_data=stage_data# ステージのコンフィグファイル
        )

    # pygame側でパネル情報（建物）を更新

    pane_result = pane.simulate(max_disp = max_disp)

    # building_config.json のパス
    building_config_path = "building_config.json"

    # 結果計算 建物倒壊数(建物番号順にリスト)、建物生存数(建物番号順にリスト)、合計スコア
    collapse_count, survive_count, total_score = result_inf.calc_building_stats(pane_result, building_config_path)
    
    import matplotlib.pyplot as plt
    # プロット（テスト）
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
