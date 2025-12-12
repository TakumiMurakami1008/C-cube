import pygame
import sys
import json
from pathlib import Path
import random

import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass
from DefineEpicenter_copy import DefineEpicenter
import DefineMagnitude
from DefineWeaknessMap import DefineWeaknessMap
from EQSimulator import EQSimulatorVariableRho
from DefinePermeabilityMap import DefinePermeabilityMap
from TsunamiSimulator import TsunamiSimulatorVariableRho
from LandslideSimulator import LandslideSimulator
import PanelManager
import result_inf

# 色設定
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,128,0)
GRAY = (128,128,128)
RED = (255,0,0)
BLUE = (0,0,255)
YELLOW = (0,255,255)
BROWN = (200,100,0)
OCEAN = (0,160,255)
RIVER = (100,255,220)
PLATEAU = (131,255,147) # 台地
DELTA = (128, 128, 0) # 三角州

# 建物の最大値
MAX_OBJECT = 3

# マップの最大値
MAX_STAGE_NUM = 3

#マップサイズ
SIZE = 500

#画面の縦横サイズ
VAR_SIZE = 600
HOR_SIZE = 600

#マージン
VAR_MARGIN_SIZE = VAR_SIZE-SIZE
HOR_MARGIN_SIZE = HOR_SIZE-SIZE

#フォントサイズ
FONT_SIZE = (VAR_MARGIN_SIZE) * 0.5 // MAX_OBJECT 

#ゲームフェーズ 0:ステージ選択, 1:建物配置, 2:シミュレーション中, 3:結果発表
flag = 0

#pygameの初期化

pygame.init()
# screen = pygame.display.set_mode((SIZE,SIZE)) #ウィンドウサイズを設定
screen = pygame.display.set_mode((HOR_SIZE,VAR_SIZE))
pygame.display.set_caption('ゆれマネ！～地震災害マネジメント・シミュレータ～') #ウィンドウのタイトルを設定

# default_font = pygame.font.SysFont(None, FONT_SIZE)
font_path = "NotoSansJP-VariableFont_wght.ttf"
font = pygame.font.Font(font_path, int(FONT_SIZE))


# ステージパラメータのクラス
class Param:
    stage_num : int # ステージ番号
    tile_width : int # タイル横幅
    tile_height : int # タイル縦幅
    tile_num : int
    GRID_SIZE : int
    VAR_GRID_NUM: int
    HOR_GRID_NUM : int

    def __init__(self):
        path = Path("../Config") / f"map_config.json"
        self.stage_num = None

        with open(path, "r", encoding="utf-8_sig") as f:
            map_data = json.load(f)
            self.tile_width = map_data["tile_width"] 
            self.tile_height = map_data["tile_height"] 

        if self.tile_width == self.tile_heightf:
            self.tile_num = self.tile_width
        else:
            if self.tile_width < self.tile_height:
                self.tile_num = self.tile_width
            else:
                self.tile_num = self.tile_height

        self.GRID_SIZE = SIZE/self.tile_num
        self.VAR_GRID_NUM = int(SIZE/self.GRID_SIZE)
        self.HOR_GRID_NUM = int(SIZE/self.GRID_SIZE)

        print("tile_num: ", self.tile_num)
        print("GRID_SIZE: ", self.GRID_SIZE)
        print("VAR_GRID_NUM: ", self.VAR_GRID_NUM)
        print("HOR_GRID_NUM: ", self.HOR_GRID_NUM)

    def set_stage_num(self, stage_num):
        self.stage_num = stage_num


# 建物オブジェクト
class Obj:
    def __init__(self, num, name, strength, score, x, y):
        self.num = num
        self.name = name
        self.strength = strength
        self.score = score
        self.pos_x = x
        self.pos_y = y
        self.first_select = False

# パネル
class Panel: 
    # # position: Coordinate     # パネルの座標（配列の場所で自動計算？）
    # has_building: bool         # 建物の有無
    # building_strength: float   # 建物がある場合、建物の強度（0~1）、-1の場合壊れている建物とする
    # shaking: float             # 地震の揺れの大きさ（例：加速度や震度）
    # waving: float　　　　　　　 # 津波の波の大きさ（例：波の高さ、勢い）
    # ground_strength: float     # 地盤の強さ（0〜1などで表現）
    # terrain_type: str          # 地形情報（例："hill", "plain", "coast", etc.）
    building_type: int         # 建物の種類（例 0: なし, 1: 家, 2: ビル, ...）
    building_strength: float   # 建物がある場合、建物の強度（0~1）、-1の場合壊れている建物とする
    shaking: float             # 受けた地震の揺れの大きさ（例：加速度や震度）
    waving: float              # 受けた津波の波の大きさ（例：波の高さ、勢い）
    ground_strength: float     # 地盤の強さ（0〜1などで表現）
    terrain_type: str          # 地形情報（例："hill", "plain", "coast", etc.）
    def __init__(self, building_type, building_strength, shaking, waving, ground_strength, terrain_type):
        self.building_type = building_type
        self.building_strength = building_strength
        self.shaking = shaking
        self.waving = waving
        self.ground_strength = ground_strength
        self.terrain_type = terrain_type

# マップ情報を保持するクラス
class SampleStage:
    def __init__(self, stage_num, Param):
        self.panel = [[None] * Param.tile_num for _ in range(Param.tile_num)] #ゲームボードを表す2次元リスト
        print(f"1:{stage_num}:{len(self.panel)}")
        self.set_field(stage_num,Param)

    def set_field(self, stage_num, Param):
            path = Path("../Config") / f"map_sample{str(stage_num)}_config.json"
            with open(path, "r", encoding="utf-8_sig") as f:
                map_sample = json.load(f)
                map_settings = map_sample["map_settings"]
                self.latitiude = map_settings["latitude_range"] 
                self.longtitude = map_settings["longitude_range"]

                self.stage_data = map_sample

                map_terrain = map_sample["terrain"]
                terrain_size = len(map_terrain)

                # print(f"第{stage_num}ステージ")

                self.panel = PanelManager.PanelManager(
                    stage_data=map_sample, # ステージのコンフィグファイル
                ).get_all_panels()
    
# ゲーム画面のオブジェクト
class SampleObject:
    def __init__(self,Param):
        self.obj_num = 3

        self.stage = None

        self.click = [[None] * Param.tile_num for _ in range(Param.tile_num)]
        
        self.start_click = [None] * Param.tile_num

        self.obj = [None] * MAX_OBJECT

        # ▼▼▼ 追加: アイテム設定ファイルの確認と生成 ▼▼▼
        #self.ensure_item_config() 
        # ▲▲▲ 追加終わり ▲▲▲

        self.set_obj_param(Param)
        # self.set_field()

        self.select_obj_num = -1 # ユーザが選択中のオブジェクト番号

        self.obj_catch = False # オブジェクトを掴んでいるかのフラグ

        self.show_result = False # シミュレーション結果を表示する状態かのフラグ

        self.field_switch = 0 # 震源地になる可能性のあるマスを表示する画面に切り替えるフラグ

    # ▼▼▼ 新規追加: 設定ファイルがない場合にデフォルトを作成するメソッド ▼▼▼
    #def ensure_item_config(self):
        #config_path = Path("../Config/item_config.json")
        #if not config_path.exists():
            #print("item_config.json が見つからないため、デフォルトを作成します。")
            # デフォルトのアイテムデータ
            #default_items = [
                #{"name": "耐震ダンパー", "rarity": "SR", "owned": False},
                #{"name": "非常食セット", "rarity": "N", "owned": False},
                #{"name": "高性能発電機", "rarity": "SSR", "owned": False},
                #{"name": "簡易トイレ", "rarity": "N", "owned": False},
                #{"name": "補強材(鉄骨)", "rarity": "R", "owned": False},
            #]
            # ディレクトリがない場合は作成（念のため）
            #config_path.parent.mkdir(parents=True, exist_ok=True)
            
            #with open(config_path, "w", encoding="utf-8") as f:
                #json.dump(default_items, f, indent=4, ensure_ascii=False)
    # ▲▲▲ 新規追加終わり ▲▲▲

    # def update(self, event, obj_catch):
    def update(self, event, Param):

        # 建物配置の変更（マウスクリック時）
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.show_result==False:
                print("click")
                if self.obj_catch:
                    x, y = event.pos #クリック位置を取得
                    print("put",x,y)
                    if x<=SIZE and y<= SIZE:
                        x //= Param.GRID_SIZE
                        y //= Param.GRID_SIZE
                        if self.put_obj(int(x),int(y)):
                            self.obj_catch = False
                            print("obj_catch=False")
                else:
                    x, y = event.pos #クリック位置を取得
                    print("select",x,y)
                    x //= Param.GRID_SIZE
                    y //= Param.GRID_SIZE
                    if self.select_obj(int(x),int(y),Param):
                        self.obj_catch = True
                        print("obj_catch=True")

        # シミュレーション実行と結果表示（スペース押下時）
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.show_result == False:
                    self.show_result = True
                    stage_num = Param.stage_num

                    for i in range (10):
                        self.draw_board_right(Param)
                        pygame.display.flip() #画面を更新して描画内容を表示
                        pygame.time.wait(20)
                        self.draw_board_left(Param)
                        pygame.display.flip() #画面を更新して描画内容を表示
                        pygame.time.wait(20)
                    
                    with open(f"../Config/map_sample{stage_num}_config.json", "r", encoding="utf-8_sig") as f:
                        stage_data = json.load(f)

                    pane = PanelManager.PanelManager(
                        panel_origin = self.stage.panel,
                        stage_data=stage_data# ステージのコンフィグファイル
                    )

                    # ===== 地震シミュ =====
                    # 震源地を決める関数
                    epicenter = DefineEpicenter.define_epicenter(
                        self.epicenter_line, 
                        self.get_stage
                    )

                    # マグニチュードを決める関数
                    magnitude = DefineMagnitude.DefineMagnitude.define_magnitude(
                        stage_data = stage_data
                    )
                    #地盤の脆さを決める関数
                    weakness_map_creator = DefineWeaknessMap(
                        stage_data = stage_data
                    )
                    weakness_map = weakness_map_creator.get_weakness_map()

                    sim_EQ = EQSimulatorVariableRho(
                        epicenter=epicenter, #震源​
                        magnitude=magnitude, #地震の規模​
                        grid_shape= (Param.tile_width, Param.tile_height), #マップのグリッド情報
                        rho_map = weakness_map, #地盤の脆さ
                        # rho_map=np.ones((grid_width, grid_height)), #地盤密度を持つ配列​
                        mu=10.0, #弾性係数​（定数）
                        dt=0.05 #定数(上げると地震の広がる規模が大きくなる)
                    )
                    shaking_map = sim_EQ.run(steps=200) #揺れの大きの最大値を持つ配列（step数を上げると地震の広がる規模が大きくなる）​
                    pane = sim_EQ.update_panels(panel_manager=pane)
                    # pane_result = pane.get_all_panels() # パネル情報（建物の破壊・非破壊）を更新

                    # ===== 津波シミュ =====
                    #波の伝わりやすさを決める関数
                    permeability_map_creator = DefinePermeabilityMap(
                        stage_data = stage_data,
                        panel_manager = pane
                    )
                    permeability_map = permeability_map_creator.get_permeability_map()

                    sim_tsunami = TsunamiSimulatorVariableRho(
                        wave_source=epicenter, #震源​
                        wave_height=magnitude*1.5, #地震の規模​ 1.5は要調整
                        grid_shape= (Param.tile_width, Param.tile_height), #マップのグリッド情報
                        spread_map = permeability_map, #地盤の脆さ
                        # rho_map=np.ones((grid_width, grid_height)), #地盤密度を持つ配列​
                        mu=10.0, #弾性係数​（定数）
                        dt=0.05 #定数(上げると地震の広がる規模が大きくなる)
                    )
                    sim_tsunami.run(steps = 200)
                    pane = sim_tsunami.update_panels(panel_manager=pane)
                    # # 波の最大値（評価用）
                    # max_wave = sim_tsunami.run(steps=200)
                    # pane_result = pane.get_all_panels() # パネル情報（建物の破壊・非破壊）を更新    
                    
                    # ===== 土砂災害シミュ =====
                    sim_landslide = LandslideSimulator(
                        panel_manager = pane,
                        stage_data = stage_data,
                        damage_radius=2,
                    )
                    sim_landslide.run(panel_manager = pane, shaking_map = shaking_map)
                    pane = sim_landslide.update_panels(panel_manager=pane)
                    pane_result = pane.get_all_panels() # パネル情報（建物の破壊・非破壊）を更新    

                    # ===== シミュ終了 =====
                    self.stage.panel = pane_result
                    self.write_text(Param)

                    # ガチャ要素
                    try:
                        with open("../Config/item_config.json", "r", encoding="utf-8") as f:
                            data = json.load(f)
                        items = data["items"]
                    
                        print("--- ガチャ開始 ---")
                        for i in range(10):
                            result = self.draw_gacha(items)
                            if result:
                                print(f"{i+1}回目: [{result['rarity']}] {result['name']} を獲得！")
                            else:
                                print(f"{i+1}回目: これ以上引けるアイテムがありません。")
                                break # アイテム切れならループを抜ける
                        print("--- ガチャ終了 ---")

                    except FileNotFoundError:
                        print("エラー: item_config.json が見つかりません。")
                    except json.JSONDecodeError:
                        print("エラー: item_config.json の中身が空か、形式が正しくありません。")

                    self.field_switch = 0

            if event.key == pygame.K_f:
                # self.get_stage = DefineEpicenter.get_stage_data(self.stage.stage_data)
                # self.epicenter_line = DefineEpicenter.calcrate_line(self.get_stage)
                # self.epicenter_area = DefineEpicenter.calcrate_area(self.get_stage)
                if self.field_switch == 0:
                    self.field_switch = 1
                elif self.field_switch == 1:
                    self.field_switch = 0

        # self.draw_board(Param)

        match self.field_switch:
            case 0:
                self.draw_board(Param)

            case 1:
                self.draw_epicenter(Param)

    def draw_board_right(self, Param):
        # screen.fill(BLACK) #画面全体を緑で塗りつぶす
        start_rect = pygame.Rect(SIZE, 0, HOR_MARGIN_SIZE, SIZE)
        pygame.draw.rect(screen, GRAY, start_rect)

        for x in range(Param.tile_num):
            for y in range(Param.tile_num):
                field = pygame.Rect(x * Param.GRID_SIZE+10, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) 

                self.set_panel_color(x, y, field)

                rect = pygame.Rect(x * Param.GRID_SIZE+10, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                pygame.draw.rect(screen, BLACK, rect, 1) #定義したrectを描画

                for i in range(MAX_OBJECT):
                    if self.is_obj(x,y, i):
                        self.draw_building(x, y, self.obj[i].name, Param)

        pygame.draw.rect(screen, GRAY, start_rect)
        for y in range(int(Param.VAR_GRID_NUM)):
            for i in range(MAX_OBJECT):
                if self.is_obj(Param.HOR_GRID_NUM-1, y, i):
                    self.draw_building(Param.HOR_GRID_NUM-1, y, self.obj[i].name, Param)

    def draw_board_left(self, Param):
        # screen.fill(BLACK) #画面全体を緑で塗りつぶす
        start_rect = pygame.Rect(SIZE, 0, HOR_MARGIN_SIZE, SIZE)
        pygame.draw.rect(screen, GRAY, start_rect)

        for x in range(Param.tile_num):
            for y in range(Param.tile_num):
                field = pygame.Rect(x * Param.GRID_SIZE-10, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) 

                self.set_panel_color(x, y, field)

                rect = pygame.Rect(x * Param.GRID_SIZE-10, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                pygame.draw.rect(screen, BLACK, rect, 1) #定義したrectを描画

                for i in range(MAX_OBJECT):
                    if self.is_obj(x,y, i):
                        self.draw_building(x, y, self.obj[i].name, Param)

        pygame.draw.rect(screen, GRAY, start_rect)
        for y in range(int(Param.VAR_GRID_NUM)):
            for i in range(MAX_OBJECT):
                if self.is_obj(Param.HOR_GRID_NUM-1, y, i):
                    self.draw_building(Param.HOR_GRID_NUM-1, y, self.obj[i].name, Param)

    # 画面の描画更新
    def draw_board(self, Param):
        # screen.fill(BLACK) #画面全体を緑で塗りつぶす
        start_rect = pygame.Rect(SIZE, 0, HOR_MARGIN_SIZE, SIZE)
        pygame.draw.rect(screen, GRAY, start_rect)

        for x in range(Param.tile_num):
            for y in range(Param.tile_num):
                field = pygame.Rect(x * Param.GRID_SIZE, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) 

                self.set_panel_color(x, y, field)

                rect = pygame.Rect(x * Param.GRID_SIZE, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                pygame.draw.rect(screen, BLACK, rect, 1) #定義したrectを描画

                if self.click[x][y] is not None:
                    rect = pygame.Rect(x * Param.GRID_SIZE, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                    pygame.draw.rect(screen, WHITE, rect, 2) #定義したrectを描画

                for i in range(MAX_OBJECT):
                    if self.is_obj(x,y, i):
                        # self.draw_stone(x, y, Param)
                        self.draw_building(x, y, self.obj[i].name, Param)

        pygame.draw.rect(screen, GRAY, start_rect)
        for y in range(int(Param.VAR_GRID_NUM)):
            if self.start_click[y] is not None:
                rect = pygame.Rect((Param.HOR_GRID_NUM-1) * Param.GRID_SIZE, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                pygame.draw.rect(screen, BLACK, rect, 2) #定義したrectを描画

            for i in range(MAX_OBJECT):
                if self.is_obj(Param.HOR_GRID_NUM-1,y, i):
                    self.draw_building(Param.HOR_GRID_NUM-1, y, self.obj[i].name, Param)

    # パネルの描画色を設定
    def set_panel_color(self, x, y, field):
        if self.stage.panel[x][y].terrain_type == "山地":
            pygame.draw.rect(screen, GREEN, field)
        elif self.stage.panel[x][y].terrain_type == "平地":
            pygame.draw.rect(screen, YELLOW, field)
        elif self.stage.panel[x][y].terrain_type == "海":
            pygame.draw.rect(screen, OCEAN, field)
        elif self.stage.panel[x][y].terrain_type == "川":
            pygame.draw.rect(screen, RIVER, field)
        elif self.stage.panel[x][y].terrain_type == "埋立地":
            pygame.draw.rect(screen, BROWN, field)
        elif self.stage.panel[x][y].terrain_type == "三角州":
            pygame.draw.rect(screen, DELTA, field)
        elif self.stage.panel[x][y].terrain_type == "台地":
            pygame.draw.rect(screen, PLATEAU, field)
        else:
            pygame.draw.rect(screen, BLACK, field)
            
    #建物を描画 TODO
    def draw_building(self, x, y, name, Param):
        stage_state = self.stage.panel[x][y].building_strength #建物があり、壊れていれば -1 を返す

        if name == "民家":
            if stage_state == -1: #壊れている
                building_image = pygame.image.load('../Images/house_broken.png')
            else:
                building_image = pygame.image.load('../Images/house.png')
        elif name == "商業ビル":
            if stage_state == -1: #壊れている
                building_image = pygame.image.load('../Images/depart_broken.png')
            else:
                building_image = pygame.image.load('../Images/depart.png')
        elif name == "発電所":
            if stage_state == -1: #壊れている
                building_image = pygame.image.load('../Images/generator_broken.png')
            else:
                building_image = pygame.image.load('../Images/generator.png')


        building_image_resize = pygame.transform.scale(building_image, (Param.GRID_SIZE, Param.GRID_SIZE))
        building_image_rect = building_image.get_rect()
        building_image_rect = (x * Param.GRID_SIZE, y * Param.GRID_SIZE)
        screen.blit(building_image_resize, building_image_rect)

    def draw_epicenter(self, Param):
        start_rect = pygame.Rect(SIZE, 0, HOR_MARGIN_SIZE, SIZE)
        pygame.draw.rect(screen, GRAY, start_rect)

        for x in range(Param.tile_num):
            for y in range(Param.tile_num):
                field = pygame.Rect(x * Param.GRID_SIZE, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) 
                
                if (self.check_epicenter(x, y, Param)):
                    pygame.draw.rect(screen, RED, field)
                else:
                    pygame.draw.rect(screen, (150, 150, 150), field)

                # if(int(self.epicenter_area[0][0]) == x and int(self.epicenter_area[0][1]) == y):
                #     pygame.draw.rect(screen, BLUE, field)
                # if(int(self.epicenter_area[1][0]) == x and int(self.epicenter_area[1][1]) == y):
                #     pygame.draw.rect(screen, YELLOW, field)
                # if(int(self.epicenter_area[2][0]) == x and int(self.epicenter_area[2][1]) == y):
                #     pygame.draw.rect(screen, GREEN, field)
                # if(int(self.epicenter_area[3][0]) == x and int(self.epicenter_area[3][1]) == y):
                #     pygame.draw.rect(screen, BROWN, field)

                # if(int(self.epicenter_area[0][1]) == x and int(self.epicenter_area[0][0]) == y):
                #     pygame.draw.rect(screen, BLUE, field)
                # if(int(self.epicenter_area[1][1]) == x and int(self.epicenter_area[1][0]) == y):
                #     pygame.draw.rect(screen, YELLOW, field)
                # if(int(self.epicenter_area[2][1]) == x and int(self.epicenter_area[2][0]) == y):
                #     pygame.draw.rect(screen, GREEN, field)
                # if(int(self.epicenter_area[3][1]) == x and int(self.epicenter_area[3][0]) == y):
                #     pygame.draw.rect(screen, BROWN, field)

                rect = pygame.Rect(x * Param.GRID_SIZE, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                pygame.draw.rect(screen, BLACK, rect, 1) #定義したrectを描画

                if self.click[x][y] is not None:
                    rect = pygame.Rect(x * Param.GRID_SIZE, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                    pygame.draw.rect(screen, WHITE, rect, 2) #定義したrectを描画

                for i in range(MAX_OBJECT):
                    if self.is_obj(x,y, i):
                        self.draw_building(x, y, self.obj[i].name, Param)

        pygame.draw.rect(screen, GRAY, start_rect)
        for y in range(int(Param.VAR_GRID_NUM)):
            if self.start_click[y] is not None:
                rect = pygame.Rect((Param.HOR_GRID_NUM-1) * Param.GRID_SIZE, y * Param.GRID_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                pygame.draw.rect(screen, BLACK, rect, 2) #定義したrectを描画

            for i in range(MAX_OBJECT):
                if self.is_obj(Param.HOR_GRID_NUM-1,y, i):
                    self.draw_building(Param.HOR_GRID_NUM-1, y, self.obj[i].name, Param)

    def check_epicenter(self, x, y, Param):
        gradient_12 = ((self.epicenter_area[0][1]) - (self.epicenter_area[1][1]))/((self.epicenter_area[0][0]) - (self.epicenter_area[1][0]))
        gradient_13 = ((self.epicenter_area[0][1]) - (self.epicenter_area[2][1]))/((self.epicenter_area[0][0]) - (self.epicenter_area[2][0]))
        gradient_24 = ((self.epicenter_area[1][1]) - (self.epicenter_area[3][1]))/((self.epicenter_area[1][0]) - (self.epicenter_area[3][0]))
        gradient_34 = ((self.epicenter_area[2][1]) - (self.epicenter_area[3][1]))/((self.epicenter_area[2][0]) - (self.epicenter_area[3][0]))

        # intercept_12 = gradient_12*(-(self.epicenter_area[0][0]+Param.GRID_SIZE)) + (self.epicenter_area[0][1]+Param.GRID_SIZE)
        # intercept_13 = gradient_13*(-(self.epicenter_area[0][0]+Param.GRID_SIZE)) + (self.epicenter_area[0][1]+Param.GRID_SIZE)
        # intercept_24 = gradient_24*(-(self.epicenter_area[1][0]+Param.GRID_SIZE)) + (self.epicenter_area[1][1]-Param.GRID_SIZE)
        # intercept_34 = gradient_34*(-(self.epicenter_area[3][0]-Param.GRID_SIZE)) + (self.epicenter_area[3][1]-Param.GRID_SIZE)

        intercept_12 = gradient_12*(-(self.epicenter_area[0][0])) + (self.epicenter_area[0][1])
        intercept_13 = gradient_13*(-(self.epicenter_area[0][0])) + (self.epicenter_area[0][1])
        intercept_24 = gradient_24*(-(self.epicenter_area[1][0])) + (self.epicenter_area[1][1])
        intercept_34 = gradient_34*(-(self.epicenter_area[3][0])) + (self.epicenter_area[3][1])

        # gradient_12 = ((self.epicenter_area[0][0]) - (self.epicenter_area[1][0]))/((self.epicenter_area[0][1]) - (self.epicenter_area[1][1]))
        # gradient_13 = ((self.epicenter_area[0][0]) - (self.epicenter_area[2][0]))/((self.epicenter_area[0][1]) - (self.epicenter_area[2][1]))
        # gradient_24 = ((self.epicenter_area[1][0]) - (self.epicenter_area[3][0]))/((self.epicenter_area[1][1]) - (self.epicenter_area[3][1]))
        # gradient_34 = ((self.epicenter_area[2][0]) - (self.epicenter_area[3][0]))/((self.epicenter_area[2][1]) - (self.epicenter_area[3][1]))

        # intercept_12 = gradient_12*(-(self.epicenter_area[0][1]+Param.GRID_SIZE)) + (self.epicenter_area[0][0]-Param.GRID_SIZE)
        # intercept_13 = gradient_13*(-(self.epicenter_area[0][1]+Param.GRID_SIZE)) + (self.epicenter_area[0][0]-Param.GRID_SIZE)
        # intercept_24 = gradient_24*(-(self.epicenter_area[1][1]+Param.GRID_SIZE)) + (self.epicenter_area[1][0]+Param.GRID_SIZE)
        # intercept_34 = gradient_34*(-(self.epicenter_area[2][1]-Param.GRID_SIZE)) + (self.epicenter_area[2][0]-Param.GRID_SIZE)

        # intercept_12 = gradient_12*(-(self.epicenter_area[0][1])) + (self.epicenter_area[0][0])
        # intercept_13 = gradient_13*(-(self.epicenter_area[0][1])) + (self.epicenter_area[0][0])
        # intercept_24 = gradient_24*(-(self.epicenter_area[1][1])) + (self.epicenter_area[1][0])
        # intercept_34 = gradient_34*(-(self.epicenter_area[2][1])) + (self.epicenter_area[2][0])

        # print("12 : y= " + str(gradient_12) + " x + " + str(intercept_12))
        # print("13 : y= " + str(gradient_13) + " x + " + str(intercept_13))
        # print("24 : y= " + str(gradient_24) + " x + " + str(intercept_24))
        # print("34 : y= " + str(gradient_34) + " x + " + str(intercept_34))

        pygame.draw.line(screen, BLACK, self.epicenter_line[0]*Param.GRID_SIZE, self.epicenter_line[1]*Param.GRID_SIZE, width=3)

        if(y <= gradient_12*x + intercept_12):
            if(y <= gradient_13*x + intercept_13):
                if(y >= gradient_24*x + intercept_24):
                    if(y >= gradient_34*x + intercept_34):

        # if(y <= gradient_12*x + intercept_12):
        #     if(y >= gradient_13*x + intercept_13):
        #         if(y <= gradient_24*x + intercept_24):
        #             if(y >= gradient_34*x + intercept_34):
        
                        # print("point " + str(x) + ", " + str(y) + " is epicenter")
                        return True
                    
        return False

    # 建物オブジェクトが選択した座標にあるか判定（プレイヤの操作時使用）
    def is_obj(self, x, y, obj_num):            
        if self.obj[obj_num].pos_x == x and self.obj[obj_num].pos_y == y:
            return True
            
        return False

    # 建物オブジェクトを掴んでいるか判定（プレイヤの操作時使用）        
    def select_obj(self, x, y, Param):
        if x < Param.tile_num:
            for i in range(self.obj_num):
                if self.is_obj(x,y,i):
                    print("select")
                    print(x,y)
                    # 建物オブジェクトを選択
                    if self.obj[i].pos_x == x and self.obj[i].pos_y == y:
                        self.select_obj_num = self.obj[i].num
                        print(self.select_obj_num)
                        self.stage.panel[x][y].building_type = -1
                    self.click[x][y] = RED
                    return True
        
        elif Param.tile_num <= x and x < HOR_SIZE:
            for i in range(MAX_OBJECT):
                if self.is_obj(x,y,i):
                    print("start_select")
                    print(x,y)
                    if self.obj[i].pos_x == x and self.obj[i].pos_y == y:
                        self.select_obj_num = self.obj[i].num
                        self.obj[i].first_select = True
                        print(self.select_obj_num)
                    self.start_click[y] = RED
                    return True
        
        return False

    # 建物オブジェクトを配置（プレイヤの操作時使用）
    def put_obj(self, x, y):
        can_put = True
        for i in range(MAX_OBJECT):
            if i != self.select_obj_num:
                if self.is_obj(x,y,i):
                    can_put = False

        if can_put:
            print("put")
            print(f"x: {x}, y: {y}")
            
            # self. board[x][y] = BLACK

            if self.obj[self.select_obj_num].first_select:
                self.obj[self.select_obj_num].first_select = False
                self.start_click[self.obj[self.select_obj_num].pos_y] = None
            else:
                # self.board[self.obj[self.select_obj_num].pos_x][self.obj[self.select_obj_num].pos_y] = None
                self.click[self.obj[self.select_obj_num].pos_x][self.obj[self.select_obj_num].pos_y] = None
            
            self.obj[self.select_obj_num].pos_x = x
            self.obj[self.select_obj_num].pos_y = y

            # TODO: ファイルから読みだした建物パラメータを設定
            print(f"self.select_obj_num: {self.select_obj_num}, name: {self.obj[self.select_obj_num].name}")
            if self.obj[self.select_obj_num].name == "民家":
                self.stage.panel[x][y].building_type = 0
                self.stage.panel[x][y].building_strength = 0.5
                print(f"(x,y):{(x,y)}, Set building_type: {self.stage.panel[x][y].building_type}")
            elif self.obj[self.select_obj_num].name == "商業ビル":
                self.stage.panel[x][y].building_type = 1
                self.stage.panel[x][y].building_strength = 0.7
            elif self.obj[self.select_obj_num].name == "発電所":
                self.stage.panel[x][y].building_type = 2
                self.stage.panel[x][y].building_strength = 1.0
            else:
                print(f"error: obj_num={self.select_obj_num}")
            # print(f"[{x}][{y}]:{self.stage.panel[x][y].building_type}")
            self.select_obj_num = -1
            return True
        return False
    
    # 建物オブジェクトのパラメータを設定
    def set_obj_param(self, Param):
        path = Path("../Config") / f"building_config.json"
        with open(path, "r", encoding="utf-8_sig") as f:
            building = json.load(f)
            for i in range(MAX_OBJECT):
                building_num = building[str(i)]
                # if i == 0:
                #     self.obj[i] = Obj(i, Param.HOR_GRID_NUM-1, i, BLACK)
                #     print("start" + str(i) + "=" + str(Param.HOR_GRID_NUM-1) + "," + str(i) + ",BLACK")
                # elif i == 1:
                #     self.obj[i] = Obj(i, Param.HOR_GRID_NUM-1, i, RED)
                #     print("start" + str(i) + "=" + str(Param.HOR_GRID_NUM-1) + "," + str(i) + ",RED")
                # elif i == 2:
                #     self.obj[i] = Obj(i, Param.HOR_GRID_NUM-1, i, BLUE)
                #     print("start" + str(i) + "=" + str(Param.HOR_GRID_NUM-1) + "," + str(i) + ",BLUE")
                # else:
                #     self.obj[i] = Obj(i, Param.HOR_GRID_NUM-1, i, YELLOW)
                #     print("start" + str(i) + "=" + str(Param.HOR_GRID_NUM-1) + "," + str(i) + ",YELLOW")

                self.obj[i] = Obj(i, building_num["name"], building_num["strength"], building_num["score"], Param.HOR_GRID_NUM-1, i) #num, name, strength, score, x, y

    # パネルの状態を描画（シミュレーション実行時に呼び出し） 
    # TODO: パネルの状態ではなく、シミュ結果を表示する，TODO: 実行後のパネルの状態を描画させる
    def write_text(self, Param):
        text_num = 0
        text_rect = pygame.Rect(0, SIZE, HOR_SIZE, VAR_MARGIN_SIZE)
        pygame.draw.rect(screen, BLACK, text_rect)

        # unbroken_building_count = 0
        # broken_building_count = 0 
        # for x in range(Param.tile_num):
        #     for y in range(Param.tile_num):
        #         # print(f"[{x},{y}]:{self.stage.panel[x][y].building_type}")
        #         if self.stage.panel[x][y].building_type >= 1: # 建物があるなら
        #             if self.stage.panel[x][y].building_strength <= 0:
        #                 broken_building_count += 1
        #             else:
        #                 unbroken_building_count += 1

        # 最終結果表示


        collapse_count, survive_count, total_score = \
            result_inf.calc_building_stats(pane_result = self.stage.panel, 
                                           building_config_path = "../Config/building_config.json"
                                           )

        # for x in range(Param.tile_num):
        #     for y in range(Param.tile_num):
        #         # print(f"[{x},{y}]:{self.stage.panel[x][y].building_type}")
        #         if self.stage.panel[x][y].building_type >= 1: # 建物があるなら
        #             # TODO 建物の状態と結果を表示
        #             text = "building_pos=" + str(x) + "," + str(y) + "," + self.stage.panel[x][y].terrain_type
        #             print(text)
        #             screen_text = font.render(text, True, WHITE)
        #             screen_pos = (10, SIZE+FONT_SIZE*text_num)
        #             screen.blit(screen_text, screen_pos)
        #             text_num = text_num+1


        text = f"壊れた建物数: {collapse_count}"
        print(text)
        screen_text = font.render(text, True, WHITE)
        screen_pos = (10, SIZE+FONT_SIZE*text_num)
        screen.blit(screen_text, screen_pos)
        text_num = text_num+1


        text = f"壊れなかった建物数: {survive_count}"
        print(text)
        screen_text = font.render(text, True, WHITE)
        screen_pos = (10, SIZE+FONT_SIZE*text_num)
        screen.blit(screen_text, screen_pos)
        text_num = text_num+1

        text = f"総合スコア: {total_score}"
        print(text)
        screen_text = font.render(text, True, WHITE)
        screen_pos = (10, SIZE+FONT_SIZE*text_num)
        screen.blit(screen_text, screen_pos)
        text_num = text_num+1



    # ステージ情報を取得
    def get_stage(self, stage_num, Param):
        self.stage = SampleStage(
            stage_num=stage_num,
            Param=Param
        )
        self.get_epicenter(self.stage)

    def get_epicenter(self, stage):
        self.get_stage = DefineEpicenter.get_stage_data(stage.stage_data)
        self.epicenter_line = DefineEpicenter.calcrate_line(self.get_stage)
        self.epicenter_area = DefineEpicenter.calcrate_area(self.get_stage)

    def read_config(self):
        path = Path("../Config") / f"building_config.json"
        with open(path, "r", encoding="utf-8_sig") as f:
            building = json.load(f)
            for i in range(MAX_OBJECT):
                map_settings = building["map_settings"]
                self.latitiude = building["latitude_range"] 
                self.longtitude = building["longitude_range"]

    #ガチャ要素(作りかけ)
    def draw_gacha(self,items):
    # 所有していないアイテムだけを対象にする
        available_items = [item for item in items if not item["owned"]]
        
        if not available_items:
            print("すべてのアイテムを所有しています！")
            return None
        
        prize = random.choice(available_items)
        prize["owned"] = True  # 所有フラグをTrueにする
        
        # JSONを更新して保存
        with open("../Config/item_config.json", "w", encoding="utf-8") as f:
            json.dump(items, f, indent=4, ensure_ascii=False)
    
        return prize

# ステージ選択画面
class StageSelect:
    def __init__(self, Param):
        self.MAX_STAGE_NUM = MAX_STAGE_NUM # ステージの総数

        self.stage_num = 0

        self.stage = [None] * self.MAX_STAGE_NUM

        for i in range(self.MAX_STAGE_NUM):
            self.stage[i] = SampleStage(
                stage_num=i,
                Param=Param
            )

    def update(self, event, Param):
        if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if self.stage_num+1 < self.MAX_STAGE_NUM:
                        self.stage_num = self.stage_num+1
                    else:
                        self.stage_num = 0

                elif event.key == pygame.K_LEFT:
                    if self.stage_num-1 >= 0:
                        self.stage_num = self.stage_num-1
                    else:
                        self.stage_num = self.MAX_STAGE_NUM-1

        self.draw_board(self.stage_num, Param)
        self.write_text(self.stage_num)

    #ボードを描画
    def draw_board(self, stage_num, Param):
        screen.fill(BLACK) #画面全体を緑で塗りつぶす
        # print(f"ステージ番号: {stage_num}, タイル数: {Param.tile_num}")
        # print(f"{self.stage[stage_num].panel}") # Nonetype

        for x in range(Param.tile_num):
            for y in range(Param.tile_num):
                field = pygame.Rect(x * Param.GRID_SIZE + HOR_MARGIN_SIZE//2, y * Param.GRID_SIZE + VAR_MARGIN_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) 
                
                # if self.stage[stage_num].panel[x][y].terrain_type == "山":
                #     pygame.draw.rect(screen, GREEN, field)
                # elif self.stage[stage_num].panel[x][y].terrain_type == "平地":
                #     pygame.draw.rect(screen, BROWN, field)
                # elif self.stage[stage_num].panel[x][y].terrain_type == "海":
                #     pygame.draw.rect(screen, OCEAN, field)
                # else:
                #     pygame.draw.rect(screen, BLACK, field)
                if self.stage[stage_num].panel[x][y].terrain_type == "山地":
                    pygame.draw.rect(screen, GREEN, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "平地":
                    pygame.draw.rect(screen, YELLOW, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "海":
                    pygame.draw.rect(screen, OCEAN, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "川":
                    pygame.draw.rect(screen, RIVER, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "埋立地":
                    pygame.draw.rect(screen, BROWN, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "三角州":
                    pygame.draw.rect(screen, DELTA, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "台地":
                    pygame.draw.rect(screen, PLATEAU, field)
                else:
                    pygame.draw.rect(screen, BLACK, field)
                
                rect = pygame.Rect(x * Param.GRID_SIZE + HOR_MARGIN_SIZE//2, y * Param.GRID_SIZE + VAR_MARGIN_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                pygame.draw.rect(screen, BLACK, rect, 1) #定義したrectを描画

                # マスに駒が置かれているか
                # if self.board[x][y] is not None:
                #     self.draw_stone(x, y, self.board[x][y]) #置かれていたら駒を描画

    def write_text(self,stage_num):
        text_rect = pygame.Rect(0, 0, HOR_SIZE, VAR_MARGIN_SIZE)
        pygame.draw.rect(screen, BLACK, text_rect)

        text = "STAGE" + str(stage_num)

        screen_text = font.render(text, True, WHITE)
        screen_pos = (HOR_SIZE//2, FONT_SIZE)
        screen.blit(screen_text, screen_pos)


def main():
    param = Param()
    stage_select = StageSelect(param)
    game = SampleObject(param) #オセロゲームのインスタンス作成
    running = True #ゲームループの制御フラグ

    window = 0

    # obj_catch = False

    #ゲームループ
    while running:

        #pygameのイベントキューからイベントを取得
        for event in pygame.event.get():

            #ウィンドウを閉じた場合、ゲームを終了
            if event.type == pygame.QUIT:
                running = False

            # エンターキーを押したとき
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    window = 1 # 建物配置画面へ移行
                    game.get_stage(stage_num=stage_select.stage_num, Param=param) # ゲーム側にステージ情報を渡す
                    param.set_stage_num(stage_select.stage_num) # ステージ番号を設定
                    screen.fill(BLACK) #画面全体を塗りつぶす

            match window:
                # ステージ選択画面のとき
                case 0:
                    stage_select.update(event, param)

                # 建物配置等画面のとき
                case 1:
                    # game.update(event, obj_catch)
                    game.update(event, param)

        pygame.display.flip() #画面を更新して描画内容を表示
    pygame.quit() #pygameを終了
    sys.exit() #プログラムを終了


#このスクリプトが直接実行された場合のみmain関数を呼び出す
if __name__ == "__main__":
    main()

# TODO: ステージ作成
# TODO: 地震の発生しうる場所を描画（）
# TODO: シミュレーションの結果を表示（描画の切り替え）(write_text 関数の書き換え)
