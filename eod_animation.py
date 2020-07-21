# encoding: utf-8

from eod_basicclasses import *


class Animation:
    anim_surfs: list
    cur_frame: int
    frame_count: int
    frame_period: float
    inner_counter: int
    frame_size: vec2

    def __init__(self, frame_count: int = 0, frame_period: float = 0.1):
        self.anim_surfs = list()
        self.cur_frame = 0
        self.frame_count = frame_count
        self.frame_period = frame_period
        self.frame_size = vec2((16, 16))
        self.inner_counter = 0

    # load animation frames from file
    def load(self, texture: Surface, row_id=0, frame_size=vec2((16, 16))):
        self.frame_size = frame_size
        self.anim_surfs = list()
        for i in range(0, self.frame_count):
            tex = texture.subsurface((int(self.frame_size.x)*i, int(self.frame_size.y)*row_id,
                                      int(self.frame_size.x), int(self.frame_size.y)))
            self.anim_surfs.append(tex)
        return self

    def update(self):
        self.inner_counter += 1
        if (GAME_DELTATIME * self.inner_counter) >= (self.frame_period / GAME_TIME_SCALE):
            self.inner_counter = 0
            self.cur_frame += 1
            if self.cur_frame >= self.frame_count:
                self.cur_frame = 0

    def get_frame(self) -> Surface:
        return self.anim_surfs[self.cur_frame]

    def add_frame(self, frame=Surface):
        self.anim_surfs.append(frame)
