import json

from Codes import *
from Data import *



## パネル情報を管理するクラス
class PanelManager:
    def __init__(self, stage_num, config_path = ""):

        # configから情報を読み取り
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.tile_width = config["tile_width"]
        self.tile_height = config["tile_height"]

        self._set_panels(stage_num = stage_num)

    def _set_panels(self, stage_num):
        
        return 1

    def update(self):
        aaa
