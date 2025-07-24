import pygame
import sys

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,128,0)
GRAY = (128,128,128)
RED = (255,0,0)
BLUE = (0,0,255)
YELLOW = (0,255,255)
BROWN = (200,100,0)
OCEAN = (0,160,255)

MAX_OBJECT = 3

#マップサイズ
SIZE = 500

#画面の縦横サイズ
VAR_SIZE = 600
HOR_SIZE = 600

VAR_MARGIN_SIZE = VAR_SIZE-SIZE
HOR_MARGIN_SIZE = HOR_SIZE-SIZE

#マップのマス目の数
BORAD_SIZE = 30

#各マスのサイズ
GRID_SIZE = SIZE/BORAD_SIZE

VAR_GRID_NUM = int(SIZE/GRID_SIZE)
HOR_GRID_NUM = int(HOR_SIZE/GRID_SIZE)

FONT_SIZE = (VAR_MARGIN_SIZE) // MAX_OBJECT

#pygameの初期化

pygame.init()
# screen = pygame.display.set_mode((SIZE,SIZE)) #ウィンドウサイズを設定
screen = pygame.display.set_mode((HOR_SIZE,VAR_SIZE))
pygame.display.set_caption('オセロ') #ウィンドウのタイトルを設定

default_font = pygame.font.SysFont(None, FONT_SIZE)

class Obj:
    def __init__(self, num, x, y, color):
        self.num = num
        self.pos_x = x
        self.pos_y = y
        self.color = color
        self.first_select = False

class Panel: #パネル
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
    def __init__(self, stage_num):
        self.panel = [[None] * BORAD_SIZE for _ in range(BORAD_SIZE)] #ゲームボードを表す2次元リスト
        
        self.set_field(stage_num)

    def set_field(self, stage_num):
            match stage_num:
                case 0:
                    for x in range(BORAD_SIZE):
                        for y in range(BORAD_SIZE):
                            self.panel[x][y] = Panel (
                                has_building = False,
                                building_strength = 1.0,
                                shaking = 0.0,
                                ground_strength = 1.0,
                                terrain_type = "hill"
                            )

                            if BORAD_SIZE // 3 < y and y <= BORAD_SIZE // 3 * 2:
                                self.panel[x][y].terrain_type = "plain"

                            elif BORAD_SIZE // 3 *2 < y:
                                self.panel[x][y].terrain_type = "ocean"

                case 1:
                    for x in range(BORAD_SIZE):
                        for y in range(BORAD_SIZE):
                            self.panel[x][y] = Panel (
                                has_building = False,
                                building_strength = 1.0,
                                shaking = 0.0,
                                ground_strength = 1.0,
                                terrain_type = "hill"
                            )

                            if 2*BORAD_SIZE // 3 < x+y and x+y <= 2*BORAD_SIZE // 3*2:
                                self.panel[x][y].terrain_type = "plain"

                            elif 2*BORAD_SIZE // 3*2 < x+y:
                                self.panel[x][y].terrain_type = "ocean"
                    
    


class SampleObject:

    def __init__(self):
        self.obj_num = 3

        # self.board = [[None] * BORAD_SIZE for _ in range(BORAD_SIZE)] #ゲームボードを表す2次元リスト
        self.click = [[None] * BORAD_SIZE for _ in range(BORAD_SIZE)]

        # self.panel = [[None] * BORAD_SIZE for _ in range(BORAD_SIZE)]
        
        self.start_click = [None] * BORAD_SIZE

        self.obj = [None] * self.obj_num

        self.put_start_obj()
        # self.set_field()

        self.select_obj_num = -1

        self.obj_catch = False

    # def update(self, event, obj_catch):
    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.obj_catch:
                x, y = event.pos #クリック位置を取得
                # print(x,y)
                if x<=SIZE and y<= SIZE:
                    x //= GRID_SIZE
                    y //= GRID_SIZE
                    if self.put_obj(int(x),int(y)):
                        self.obj_catch = False
                        print("obj_catch=False")
                # x //= GRID_SIZE
                # y //= GRID_SIZE
                # if game.put_obj(int(x),int(y)):
                #     obj_catch = False
            else:
                x, y = event.pos #クリック位置を取得
                # if x<= SIZE and y <= SIZE:
                #     x //= GRID_SIZE
                #     y //= GRID_SIZE
                #     if game.select_obj(int(x),int(y)):
                #         obj_catch = True
                x //= GRID_SIZE
                y //= GRID_SIZE
                if self.select_obj(int(x),int(y)):
                    self.obj_catch = True
                    print("obj_catch=True")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.write_text()

        self.draw_board()


    #ボードを描画
    def draw_board(self):
        # screen.fill(BLACK) #画面全体を緑で塗りつぶす
        start_rect = pygame.Rect(SIZE, 0, HOR_MARGIN_SIZE, SIZE)
        pygame.draw.rect(screen, GRAY, start_rect)

        for x in range(BORAD_SIZE):
            for y in range(BORAD_SIZE):
                field = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE) 
                
                # if self.panel[x][y].terrain_type == "hill":
                #     pygame.draw.rect(screen, GREEN, field)
                # elif self.panel[x][y].terrain_type == "plain":
                #     pygame.draw.rect(screen, BROWN, field)
                # elif self.panel[x][y].terrain_type == "ocean":
                #     pygame.draw.rect(screen, OCEAN, field)

                if self.stage.panel[x][y].terrain_type == "hill":
                    pygame.draw.rect(screen, GREEN, field)
                elif self.stage.panel[x][y].terrain_type == "plain":
                    pygame.draw.rect(screen, BROWN, field)
                elif self.stage.panel[x][y].terrain_type == "ocean":
                    pygame.draw.rect(screen, OCEAN, field)

                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                pygame.draw.rect(screen, BLACK, rect, 1) #定義したrectを描画

                if self.click[x][y] is not None:
                    rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                    pygame.draw.rect(screen, WHITE, rect, 2) #定義したrectを描画

                # マスに駒が置かれているか
                # if self.board[x][y] is not None:
                #     self.draw_stone(x, y, self.board[x][y]) #置かれていたら駒を描画

                for i in range(self.obj_num):
                    if self.is_obj(x,y, i):
                        self.draw_stone(x, y, self.obj[i].color)

        pygame.draw.rect(screen, GRAY, start_rect)
        for y in range(int(VAR_GRID_NUM)):
            if self.start_click[y] is not None:
                rect = pygame.Rect((HOR_GRID_NUM-1) * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
                pygame.draw.rect(screen, BLACK, rect, 2) #定義したrectを描画

            for i in range(self.obj_num):
                if self.is_obj(HOR_GRID_NUM-1,y, i):
                    self.draw_stone(HOR_GRID_NUM-1, y, self.obj[i].color)

    #駒を描画
    def draw_stone(self, x, y, color):
        pygame.draw.circle(screen, color, (x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 2 - 4)

    def is_obj(self, x, y, obj_num):

        #駒が置かれている場合は置けない
        # if self.board[x][y] is not None:
        #     return True
        # else:
        #     return False
        
        # for i in range(self.obj_num):
        #     if self.obj[i].pos_x == x and self.obj[i].pos_y == y:
        #         return True
            
        if self.obj[obj_num].pos_x == x and self.obj[obj_num].pos_y == y:
            return True
            
        return False
        
    def select_obj(self, x, y):
        if x < BORAD_SIZE:
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
        
        elif BORAD_SIZE <= x and x < HOR_SIZE:
            for i in range(self.obj_num):
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

    def put_obj(self, x, y):
        can_put = True
        for i in range(self.obj_num):
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
    
    def put_start_obj(self):
        for i in range(self.obj_num):
            if i == 0:
                self.obj[i] = Obj(i, HOR_GRID_NUM-1, i, BLACK)
                print("start" + str(i) + "=" + str(HOR_GRID_NUM-1) + "," + str(i) + ",BLACK")
            elif i == 1:
                self.obj[i] = Obj(i, HOR_GRID_NUM-1, i, RED)
                print("start" + str(i) + "=" + str(HOR_GRID_NUM-1) + "," + str(i) + ",RED")
            elif i == 2:
                self.obj[i] = Obj(i, HOR_GRID_NUM-1, i, BLUE)
                print("start" + str(i) + "=" + str(HOR_GRID_NUM-1) + "," + str(i) + ",BLUE")
            else:
                self.obj[i] = Obj(i, HOR_GRID_NUM-1, i, YELLOW)
                print("start" + str(i) + "=" + str(HOR_GRID_NUM-1) + "," + str(i) + ",YELLOW")

    # def set_field(self):
    #     for x in range(BORAD_SIZE):
    #         for y in range(BORAD_SIZE):
    #             self.panel[x][y] = Panel (
    #                 has_building = False,
    #                 building_strength = 1.0,
    #                 shaking = 0.0,
    #                 ground_strength = 1.0,
    #                 terrain_type = "hill"
    #             )

    #             if BORAD_SIZE // 3 < y and y <= BORAD_SIZE // 3 * 2:
    #                 self.panel[x][y].terrain_type = "plain"

    #             elif BORAD_SIZE // 3 *2 < y:
    #                 self.panel[x][y].terrain_type = "ocean"

    def write_text(self):
        text_num = 0
        text_rect = pygame.Rect(0, SIZE, HOR_SIZE, VAR_MARGIN_SIZE)
        pygame.draw.rect(screen, BLACK, text_rect)
        for x in range(BORAD_SIZE):
            for y in range(BORAD_SIZE):
                if self.stage.panel[x][y].has_building == True:
                    text = "building_pos=" + str(x) + "," + str(y) + "," + self.stage.panel[x][y].terrain_type
                    print(text)
                    screen_text = default_font.render(text, True, WHITE)
                    screen_pos = (10, SIZE+FONT_SIZE*text_num)
                    screen.blit(screen_text, screen_pos)
                    text_num = text_num+1

    def get_stage(self, stage_num):
        self.stage = SampleStage(
            stage_num=stage_num
        )

                    

class StageSelect:
    def __init__(self):
        self.MAX_STAGE_NUM = 2

        self.stage_num = 0

        self.stage = [None] * self.MAX_STAGE_NUM

        for i in range(self.MAX_STAGE_NUM):
            self.stage[i] = SampleStage(
                stage_num=i
            )

    def update(self, event):
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

        self.draw_board(self.stage_num)
        self.write_text(self.stage_num)

    #ボードを描画
    def draw_board(self, stage_num):
        screen.fill(BLACK) #画面全体を緑で塗りつぶす

        for x in range(BORAD_SIZE):
            for y in range(BORAD_SIZE):
                field = pygame.Rect(x * GRID_SIZE + HOR_MARGIN_SIZE//2, y * GRID_SIZE + VAR_MARGIN_SIZE, GRID_SIZE, GRID_SIZE) 
                
                if self.stage[stage_num].panel[x][y].terrain_type == "hill":
                    pygame.draw.rect(screen, GREEN, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "plain":
                    pygame.draw.rect(screen, BROWN, field)
                elif self.stage[stage_num].panel[x][y].terrain_type == "ocean":
                    pygame.draw.rect(screen, OCEAN, field)

                rect = pygame.Rect(x * GRID_SIZE + HOR_MARGIN_SIZE//2, y * GRID_SIZE + VAR_MARGIN_SIZE, GRID_SIZE, GRID_SIZE) #各マスの位置とサイズを定義するためのrectを作成
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
    stage_select = StageSelect()
    game = SampleObject() #オセロゲームのインスタンス作成
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    window = 1
                    game.get_stage(stage_select.stage_num)
                    screen.fill(BLACK) #画面全体を緑で塗りつぶす

            match window:
                case 0:
                    stage_select.update(event)

                case 1:
                    # game.update(event, obj_catch)
                    game.update(event)

            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     if obj_catch:
            #         x, y = event.pos #クリック位置を取得
            #         # print(x,y)
            #         if x<=SIZE and y<= SIZE:
            #             x //= GRID_SIZE
            #             y //= GRID_SIZE
            #             if game.put_obj(int(x),int(y)):
            #                 obj_catch = False
            #                 print("obj_catch=False")
            #         # x //= GRID_SIZE
            #         # y //= GRID_SIZE
            #         # if game.put_obj(int(x),int(y)):
            #         #     obj_catch = False
            #     else:
            #         x, y = event.pos #クリック位置を取得
            #         # if x<= SIZE and y <= SIZE:
            #         #     x //= GRID_SIZE
            #         #     y //= GRID_SIZE
            #         #     if game.select_obj(int(x),int(y)):
            #         #         obj_catch = True
            #         x //= GRID_SIZE
            #         y //= GRID_SIZE
            #         if game.select_obj(int(x),int(y)):
            #             obj_catch = True
            #             print("obj_catch=True")

            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         game.write_text()


        # game.draw_board()
        pygame.display.flip() #画面を更新して描画内容を表示
    pygame.quit() #pygameを終了
    sys.exit() #プログラムを終了


#このスクリプトが直接実行された場合のみmain関数を呼び出す
if __name__ == "__main__":
    main()
