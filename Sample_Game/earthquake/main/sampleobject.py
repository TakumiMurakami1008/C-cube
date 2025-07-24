import pygame
import sys

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,128,0)
GRAY = (128,128,128)
RED = (255,0,0)
BLUE = (0,0,255)
YELLOW = (0,255,255)

MAX_OBJECT = 3

#画面サイズ
SIZE = 600

VAR_SIZE = 600
HOR_SIZE = 700

#ボードのマス目の数
BORAD_SIZE = 10

#各マスのサイズ
GRID_SIZE = SIZE/BORAD_SIZE

VAR_GRID_NUM = int(VAR_SIZE/GRID_SIZE)
HOR_GRID_NUM = int(HOR_SIZE/GRID_SIZE)

#pygameの初期化

pygame.init()
# screen = pygame.display.set_mode((SIZE,SIZE)) #ウィンドウサイズを設定
screen = pygame.display.set_mode((HOR_SIZE,VAR_SIZE))
pygame.display.set_caption('オセロ') #ウィンドウのタイトルを設定

class Obj:
    def __init__(self, num, x, y, color):
        self.num = num
        self.pos_x = x
        self.pos_y = y
        self.color = color
        self.first_select = False

class SampleObject:

    def __init__(self):
        self.obj_num = 3

        self.board = [[None] * BORAD_SIZE for _ in range(BORAD_SIZE)] #ゲームボードを表す2次元リスト
        self.click = [[None] * BORAD_SIZE for _ in range(BORAD_SIZE)]
        
        self.start_click = [None] * BORAD_SIZE

        self.obj = [None] * self.obj_num

        self.put_start_obj()

        self.select_obj_num = -1

    #ボードを描画
    def draw_board(self):
        screen.fill(GREEN) #画面全体を緑で塗りつぶす
        start_rect = pygame.Rect(SIZE, 0, HOR_SIZE-SIZE, VAR_SIZE)
        pygame.draw.rect(screen, GRAY, start_rect)
        for x in range(BORAD_SIZE):
            for y in range(BORAD_SIZE):
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
            self. board[x][y] = BLACK

            if self.obj[self.select_obj_num].first_select:
                self.obj[self.select_obj_num].first_select = False
            else:
                self.board[self.obj[self.select_obj_num].pos_x][self.obj[self.select_obj_num].pos_y] = None
                self.click[self.obj[self.select_obj_num].pos_x][self.obj[self.select_obj_num].pos_y] = None
            
            self.obj[self.select_obj_num].pos_x = x
            self.obj[self.select_obj_num].pos_y = y

            print(self.select_obj_num)
            self.start_click[y] = None
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
            

def main():
    game = SampleObject() #オセロゲームのインスタンス作成
    running = True #ゲームループの制御フラグ

    obj_catch = False

    #ゲームループ
    while running:

        #pygameのイベントキューからイベントを取得
        for event in pygame.event.get():

            #ウィンドウを閉じた場合、ゲームを終了
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if obj_catch:
                    x, y = event.pos #クリック位置を取得
                    # print(x,y)
                    if x<=SIZE and y<= SIZE:
                        x //= GRID_SIZE
                        y //= GRID_SIZE
                        if game.put_obj(int(x),int(y)):
                            obj_catch = False
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
                    if game.select_obj(int(x),int(y)):
                        obj_catch = True
                        print("obj_catch=True")

        game.draw_board()
        pygame.display.flip() #画面を更新して描画内容を表示
    pygame.quit() #pygameを終了
    sys.exit() #プログラムを終了


#このスクリプトが直接実行された場合のみmain関数を呼び出す
if __name__ == "__main__":
    main()
