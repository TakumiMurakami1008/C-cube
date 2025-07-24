import pygame
import sys
import json
from pathlib import Path

from dataclasses import dataclass
import DefineEpicenter
import DefineMagnitude
from DefineWeaknessMap import DefineWeaknessMap
from EQSimulator import EQSimulatorVariableRho
import PanelManager

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

# 建物の最大値
MAX_OBJECT = 3

#マップサイズ
SIZE = 500

#画面の縦横サイズ
VAR_SIZE = 600
HOR_SIZE = 600

#マージン
VAR_MARGIN_SIZE = VAR_SIZE-SIZE
HOR_MARGIN_SIZE = HOR_SIZE-SIZE

#フォントサイズ
FONT_SIZE = (VAR_MARGIN_SIZE) // MAX_OBJECT

#pygameの初期化

pygame.init()
# screen = pygame.display.set_mode((SIZE,SIZE)) #ウィンドウサイズを設定
screen = pygame.display.set_mode((HOR_SIZE,VAR_SIZE))
pygame.display.set_caption('ゆれマネ！～地震災害マネジメント・シミュレータ～') #ウィンドウのタイトルを設定

default_font = pygame.font.SysFont(None, FONT_SIZE)

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
        stage_num = 0
        with open(path, "r", encoding="utf-8_sig") as f:
            map_data = json.load(f)
            self.tile_width = map_data["tile_width"] 
            self.tile_height = map_data["tile_height"] 

        if self.tile_width == self.tile_height:
            self.tile_num = self.tile_width
        else:
            if self.tile_width < self.tile_height:
                self.tile_num = self.tile_width
            else:
                self.tile_num = self.tile_height

        self.GRID_SIZE = SIZE/self.tile_num
        self.VAR_GRID_NUM = int(SIZE/self.GRID_SIZE)
        self.HOR_GRID_NUM = int(HOR_SIZE/self.GRID_SIZE)

        print("tile_num: ", self.tile_num)
        print("GRID_SIZE: ", self.GRID_SIZE)
        print("VAR_GRID_NUM: ", self.VAR_GRID_NUM)
        print("HOR_GRID_NUM: ", self.HOR_GRID_NUM)

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
    # position: Coordinate     # パネルの座標（配列の場所で自動計算？）
    has_building: bool         # 建物の有無
    building_strength: float   # 建物がある場合、建物の強度（0~1）、-1の場合壊れている建物とする
    shaking: float             # 地震の揺れの大きさ（例：加速度や震度）
    ground_strength: float     # 地盤の強さ（0〜1などで表現）
    terrain_type: str          # 地形情報（例："hill", "plain", "coast", etc.）

    def __init__(self, has_building, building_strength, shaking, ground_strength, terrain_type):
        self.has_building = has_building
        self.building_strength = building_strength
        self.shaking = shaking
        self.ground_strength = ground_strength
        self.terrain_type = terrain_type

class SampleStage:
    def __init__(self, stage_num, Param):
        self.panel = [[None] * Param.tile_num for _ in range(Param.tile_num)] #ゲームボードを表す2次元リスト
        
        self.set_field(stage_num,Param)

    def set_field(self, stage_num, Param):
            path = Path("../Config") / f"map_sample{str(stage_num)}_config.json"
            with open(path, "r", encoding="utf-8_sig") as f:
                map_sample = json.load(f)
                map_settings = map_sample["map_settings"]
                self.latitiude = map_settings["latitude_range"] 
                self.longtitude = map_settings["longitude_range"]

                map_terrain = map_sample["terrain"]
                terrain_size = len(map_terrain)

                self.panel = PanelManager.PanelManager(
                    map_data=map_data, # マップのコンフィグファイル
                    stage_data=map_sample# ステージのコンフィグファイル
                )

            #     for i in range(terrain_size):
            #         get_terrain = map_terrain[i]

            #         terrian_x_start = int(get_terrain["area"][0][0] * Param.tile_num)
            #         terrian_x_end = int(get_terrain["area"][0][1] * Param.tile_num)
            #         terrian_y_start = int(get_terrain["area"][1][0] * Param.tile_num)
            #         terrian_y_end = int(get_terrain["area"][1][1] * Param.tile_num)

            #         for x in range(terrian_x_start, terrian_x_end):
            #             for y in range(terrian_y_start, terrian_y_end):
            #                 self.panel[x][y] = Panel (
            #                     has_building = False,
            #                     building_strength = 1.0,
            #                     shaking = 0.0,
            #                     ground_strength = get_terrain["weakness"],
            #                     terrain_type = get_terrain["type"]
            #                 )
            #                 # print(x,y,self.panel[x][y].terrain_type)

            # for x in range(Param.tile_num):
            #     for y in range(Param.tile_num):
            #         if(self.panel[x][y] == None):
            #             self.panel[x][y] = Panel (
            #                 has_building = False,
            #                 building_strength = 1.0,
            #                 shaking = 0.0,
            #                 ground_strength = 0.0,
            #                 terrain_type = "その他"
            #             )
    
# ゲーム画面のオブジェクト
class SampleObject:
    def __init__(self,Param):
        self.obj_num = 3

        self.click = [[None] * Param.tile_num for _ in range(Param.tile_num)]
        
        self.start_click = [None] * Param.tile_num

        self.obj = [None] * MAX_OBJECT

        self.set_obj_param(Param)
        # self.set_field()

        self.select_obj_num = -1

        self.obj_catch = False

        self.show_result = False

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

                    # TODO
                    #マップ情報取得
                    file_path = Path("../Config") / f"map_config.json"
                    with open(file_path, "r", encoding="utf-8_sig") as f:
                        map_data = json.load(f)
                        grid_width = map_data["grid_width"] 
                        grid_height = map_data["grid_height"] 

                    stage_num = Param.stage_num
                    
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
                            grid_shape= (grid_width, grid_height),
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
                    self.write_text(Param)

        self.draw_board(Param)


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
        if self.stage.panel[x][y].terrain_type == "山":
            pygame.draw.rect(screen, GREEN, field)
        elif self.stage.panel[x][y].terrain_type == "平地":
            pygame.draw.rect(screen, BROWN, field)
        elif self.stage.panel[x][y].terrain_type == "海":
            pygame.draw.rect(screen, OCEAN, field)
        else:
            pygame.draw.rect(screen, BLACK, field)

    #建物を描画 TODO
    def draw_building(self, x, y, name, Param):

        if name == "民家":
            building_image = pygame.image.load('Images/house.png')
        elif name == "商業ビル":
            building_image = pygame.image.load('Images/depart.png')
        elif name == "発電所":
            building_image = pygame.image.load('Images/generator.png')
        
        
        building_image_resize = pygame.transform.scale(building_image, (Param.GRID_SIZE, Param.GRID_SIZE))
        building_image_rect = building_image.get_rect()
        building_image_rect = (x * Param.GRID_SIZE, y * Param.GRID_SIZE)
        screen.blit(building_image_resize, building_image_rect)

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
                    if self.obj[i].pos_x == x and self.obj[i].pos_y == y:
                        self.select_obj_num = self.obj[i].num
                        print(self.select_obj_num)
                        self.stage.panel[x][y].has_building = False
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
            print(x,y)
            # self. board[x][y] = BLACK

            if self.obj[self.select_obj_num].first_select:
                self.obj[self.select_obj_num].first_select = False
                self.start_click[self.obj[self.select_obj_num].pos_y] = None
            else:
                # self.board[self.obj[self.select_obj_num].pos_x][self.obj[self.select_obj_num].pos_y] = None
                self.click[self.obj[self.select_obj_num].pos_x][self.obj[self.select_obj_num].pos_y] = None
            
            self.obj[self.select_obj_num].pos_x = x
            self.obj[self.select_obj_num].pos_y = y

            print(self.select_obj_num)
            self.stage.panel[x][y].has_building = True
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
        for x in range(Param.tile_num):
            for y in range(Param.tile_num):
                if self.stage.panel[x][y].has_building == True:
                    text = "building_pos=" + str(x) + "," + str(y) + "," + self.stage.panel[x][y].terrain_type
                    print(text)
                    screen_text = default_font.render(text, True, WHITE)
                    screen_pos = (10, SIZE+FONT_SIZE*text_num)
                    screen.blit(screen_text, screen_pos)
                    text_num = text_num+1

    # ステージ情報を取得
    def get_stage(self, stage_num,Param):
        self.stage = SampleStage(
            stage_num=stage_num,
            Param=Param
        )

    def read_config(self):
        path = Path("../Config") / f"building_config.json"
        with open(path, "r", encoding="utf-8_sig") as f:
            building = json.load(f)
            for i in range(MAX_OBJECT):
                map_settings = building["map_settings"]
                self.latitiude = building["latitude_range"] 
                self.longtitude = building["longitude_range"]

# ステージ選択画面
class StageSelect:
    def __init__(self, Param):
        self.MAX_STAGE_NUM = 3 # ステージの総数

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

        for x in range(Param.tile_num):
            for y in range(Param.tile_num):
                field = pygame.Rect(x * Param.GRID_SIZE + HOR_MARGIN_SIZE//2, y * Param.GRID_SIZE + VAR_MARGIN_SIZE, Param.GRID_SIZE, Param.GRID_SIZE) 
                
                if self.stage[stage_num].panel[x][y].terrain_type == "山":
                    pygame.draw.rect(screen, GREEN, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "平地":
                    pygame.draw.rect(screen, BROWN, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "海":
                    pygame.draw.rect(screen, OCEAN, field)
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

        screen_text = default_font.render(text, True, WHITE)
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
                    game.get_stage(stage_select.stage_num, param) # ゲーム側にステージ情報を渡す
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

# TODO: 地震の発生しうる場所を描画
# TODO: シミュレーションの結果を表示（描画の切り替え）
# TODO: stage_numをステージ選択画面からParamに与える
