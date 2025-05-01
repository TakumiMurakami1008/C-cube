import pygame
from pygame.locals import *
import sys

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
        
        # イベント処理
        # for event in pygame.event.get():
        #     if event.type == QUIT:  # 閉じるボタンが押されたら終了
        #         pygame.quit()       # Pygameの終了(画面閉じられる)
        #         sys.exit()


if __name__ == "__main__":
    main()
