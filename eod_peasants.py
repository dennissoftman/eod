# encoding: utf-8

from eod_basicclasses import *
from eod_animation import Animation


class Peasant(Object2D):
    move_speed: float = 1
    is_moving: bool = False
    is_gathering: bool = False
    is_wandering: bool = False
    is_move_finished: bool = True
    is_selected: bool = False
    target_pos: vec2 = vec2()
    wandering_pos: vec2 = vec2()
    wandering_radius: float = 0
    specialization: str = str()
    gender: str = "man"
    inventory_capacity: float = 1
    gather_period: float = 1
    inventory: list = list()
    gather_obj = None
    camp_obj = None
    direction = vec2()

    anims: dict
    cur_anim: str = "idle"
    inner_counter: int = 0

    name: str = str()
    desc_text: Text2D

    def __init__(self, win_surface: Surface = None, pos=vec2(), dim=vec2(), texture=None):
        super().__init__(win_surface=win_surface, pos=pos, dim=dim, texture=texture)

        if texture is not None:
            self.load_textures(texture)

    def load_textures(self, texture: Surface):
        assert(texture is not None)

        self.anims = dict()

        self.anims["idle_f"] = Animation(1, 0)
        self.anims["idle_f"].load(texture, row_id=0, frame_size=vec2((16, 16)))
        self.anims["idle_b"] = Animation(1, 0)
        self.anims["idle_b"].load(texture, row_id=1, frame_size=vec2((16, 16)))

        self.anims["walk_f"] = Animation(8, 0.1)
        self.anims["walk_f"].load(texture, row_id=0, frame_size=vec2((16, 16)))
        self.anims["walk_b"] = Animation(8, 0.1)
        self.anims["walk_b"].load(texture, row_id=1, frame_size=vec2((16, 16)))

    def set_name(self, name: str, gender: str = "man"):
        self.name = name
        self.gender = gender
        self.desc_text = Text2D(win_surface=self.targetSurf, size=16)
        self.desc_text.set_text(tr(self.name.lower()).capitalize() + ", " + tr(self.specialization + self.gender))

    def move_to(self, pos: vec2):
        self.target_pos = pos
        self.is_moving = True
        self.is_wandering = False
        self.is_gathering = False
        self.move_speed = MOVE_SPEED

    def gather_at(self, r: Resource):
        if r.empty():
            return
        else:
            self.is_moving = True
            self.is_wandering = False
            self.is_gathering = True
            self.gather_obj = r
            self.target_pos = self.gather_obj.pos
            self.move_speed = MOVE_SPEED

    def wander_at(self, pos: vec2, r: float = 0):
        self.wandering_pos = pos
        self.is_moving = True
        self.is_wandering = True
        self.is_gathering = False
        if r > 0:
            self.wandering_radius = r
        self.move_speed = WANDER_SPEED

    def assign(self, spec: str = str(), gather_period: float = 1.0, capacity: int = 1):
        self.specialization = spec
        self.gather_period = gather_period
        self.inventory_capacity = capacity

    def finish_dist(self) -> float:
        return (self.dim*0.25).__len__()

    def update_animation(self):
        if self.is_moving:
            self.cur_anim = "walk"
        else:
            self.cur_anim = "idle"

        if self.direction.y >= 0:
            self.cur_anim += "_f"
        else:
            self.cur_anim += "_b"

        self.anims[self.cur_anim].update()
        self.selfSurf = pyscale(self.anims[self.cur_anim].get_frame(), self.dim.data())

    def update(self):
        delta: vec2 = (self.target_pos - self.pos).normalized()
        self.direction = delta.normalized()
        self.update_animation()

        if (self.target_pos - self.pos).__len__() <= self.finish_dist():
            self.target_pos = self.pos
            self.is_move_finished = True
        else:
            self.pos += delta * self.move_speed * GAME_DELTATIME * GAME_TIME_SCALE

        if not self.is_move_finished:
            return

        if self.is_gathering:
            if self.gather_obj is None:
                self.wander_at(self.pos)
                self.update()
                return

            if abs(self.pos-self.gather_obj.pos).__len__() < self.finish_dist():
                if self.gather_obj.empty():
                    self.wander_at(self.pos + vec2((randfloat(0.5, 1), randfloat(0.5, 1)) * 50))
                    self.update()
                    return
                self.inner_counter += 1
                if (GAME_DELTATIME * self.inner_counter) >= (self.gather_period / GAME_TIME_SCALE):
                    self.inner_counter = 0
                    self.inventory.append(self.gather_obj.take(self.inventory_capacity))
                    self.target_pos = self.camp_obj.pos
            elif abs(self.pos-self.camp_obj.pos).__len__() < self.finish_dist():
                self.target_pos = self.gather_obj.pos
                for el in self.inventory:
                    self.camp_obj.res_amounts[el[0]] += el[1]
                self.inventory.clear()
            return

        if self.is_wandering:
            self.inner_counter += 1
            self.is_moving = False
            if (GAME_DELTATIME * self.inner_counter) >= (randfloat(0.5, 1.5) / GAME_TIME_SCALE):
                self.inner_counter = 0
                self.target_pos = (self.wandering_pos + vec2((randfloat(-0.5, 0.5), randfloat(-0.5, 0.5))) * self.wandering_radius)
                self.is_moving = True
                self.is_move_finished = False

    def draw(self):
        super().draw()  # for now

        if self.is_selected:
            if self.is_moving:
                pyrender.line(self.targetSurf, G_GREEN, self.pos.data(), self.target_pos.data())
            self.desc_text.pos = vec2((self.pos.x, self.pos.y - self.dim.y + 4))
            self.desc_text.draw()


def peasant_get_depth_sort(a: Peasant) -> float:
    return a.pos.y