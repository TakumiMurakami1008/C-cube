import pygame
from pygame.locals import *
import sys
from Codes import *
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
    pygame.init()                                   # Pygameの初期化
    screen = pygame.display.set_mode((400, 300))    # 400 x 300の大きさの画面を作る
    pygame.display.set_caption("Game")              # 画面上部に表示するタイトルを設定

    # データ読み込み
    # TODO

    
    

    while (1): # メインループ
        # pygame.display.update()     # 画面を更新
        
        # シミュレータ起動
        # TODO
        
        sim = EQSimulatorVariableRho(
                epicenter=(50, 50), #震源​
                magnitude=10, #地震の規模​
                grid_shape=(400, 300), #領域サイズ​
                rho_map=rho, #地盤密度を持つ配列​
                mu=1.0, #弾性係数​
                dt=0.05
            )
        max_disp = sim.run(steps=100) #揺れの大きの最大値を持つ配列​

        pane = PanelManager(
            stage_num= 0, 
            config_path = "../Config.map_config.json", # マップ共通のコンフィグを想定
            grid_shape= (400, 300), 
            )
        panel_map = pane.simulate(max_disp = max_disp)
        
        # イベント処理
        # for event in pygame.event.get():
        #     if event.type == QUIT:  # 閉じるボタンが押されたら終了
        #         pygame.quit()       # Pygameの終了(画面閉じられる)
        #         sys.exit()


if __name__ == "__main__":
    main()
