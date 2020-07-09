import pygame
from random import randint as rand
from random import uniform as randfloat

import yaml
import copy

from eod_primitives import *
from eod_config import *
from eod_tr import tr
from eod_events import event_processor

#
MEN_NAMES = ["Aaron", "Abel", "Adrian", "Alfred", "Andrew", "Arnold", "Arthur",
             "Ben", "Bill", "Bert", "Bradley",
             "Chuck", "Caleb", "Calvin", "Casey", "Christian",
             "Dennis", "Daniel", "Donald", "Douglas", "Doyle"]
WOMEN_NAMES = ["Ada", "Aggie", "Adele", "Ariana", "Anastasia", "Amelia",
               "Barbara", "Blair", "Brenda", "Bertha", "Beatrix",
               "Clair", "Carmen", "Cassandra", "Celia", "Celine",
               "Daisy", "Donna", "Dora", "Dorothy",
               "Erin", "Ellen", "Ella", "Estella", "Elza",
               "Felicia", "Florence",
               "Gabrielle", "Gina", "Grace"]
#


class Object2D:
    pos: vec2
    dim: vec2
    selfSurf: pygame.Surface = None
    targetSurf: pygame.Surface

    color: icolor

    def __init__(self, win_surface: pygame.Surface = None,
                 pos=vec2(), dim=vec2(),
                 texture: pygame.Surface = None):
        self.targetSurf = win_surface
        self.pos = pos
        self.dim = dim
        if texture is None:
            self.selfSurf = pygame.Surface(self.dim.data())
        else:
            self.selfSurf = pygame.transform.scale(texture, self.dim.data())

        self.color = icolor()
        for y in range(0, int(self.dim.y)):
            for x in range(0, int(self.dim.x)):
                col = self.selfSurf.get_at((x, y))[:3]
                if col == G_BLACK:
                    continue
                self.color.mix(icolor(col))

    def update(self):
        pass

    def draw(self):
        if GAME_RENDERMODE == 1:
            self.targetSurf.blit(self.selfSurf, (round(self.pos.x - self.dim.x*0.5), round(self.pos.y - self.dim.y*0.5)))
        else:
            pygame.draw.rect(self.targetSurf,
                             self.color.data(),
                             (round(self.pos.x - self.dim.x*0.5), round(self.pos.y-self.dim.y*0.5),
                              round(self.dim.x), round(self.dim.y)))


class Text2D:
    pos: vec2
    size: int
    text: str
    color: icolor
    target_surf: pygame.Surface
    text_surf: pygame.Surface

    def __init__(self, win_surface: pygame.Surface = None, pos=vec2(), size=16, text=str()):
        self.pos = pos
        self.size = size
        self.text = text
        self.target_surf = win_surface
        self.color = icolor((0, 0, 0))

    def set_text(self, text: str = str()):
        self.text = text
        self.update()

    def update(self):
        font = pygame.font.Font("font/uni_times.ttf", self.size)
        self.text_surf = font.render(self.text, False, self.color.data())

    def draw(self):
        self.target_surf.blit(self.text_surf, self.pos.data())


# game-related classes
WANDER_SPEED = 40
MOVE_SPEED = 100


class Resource(Object2D):
    r_id: int = 0
    r_name: str = str()
    r_type: str = str()
    capacity: float = 0
    quantity: float = 0
    partCount: int = 0
    partSurfs: list
    is_refreshable: bool = False
    refresh_time: float = 0.0

    is_selected: bool = False

    desc_text: Text2D

    inner_counter: int = 0

    def __init__(self, win_surface: pygame.Surface = None,
                 pos=vec2(), dim=vec2(),
                 texture: pygame.Surface = None):
        super().__init__(win_surface=win_surface, pos=pos, dim=dim, texture=texture)
        self.desc_text = Text2D(win_surface=self.targetSurf, size=16)

    def set_res(self, r_id, r_name, r_type):
        self.r_id = r_id
        self.r_name = r_name
        self.r_type = r_type

        self.desc_text.set_text(tr(self.r_name))
        self.desc_text.update()

    def load_parts(self, texture: pygame.Surface, count: int):
        assert(count > 0)
        self.partCount = count
        self.partSurfs = list()
        tex_dim: vec2 = vec2(texture.get_size()[0] // self.partCount, texture.get_size()[1])
        for i in range(0, self.partCount):
            tex = texture.subsurface((int(tex_dim.x) * i, 0, int(tex_dim.x), int(tex_dim.y)))
            self.partSurfs.append(pygame.transform.scale(tex, self.dim.data()))

    def fill(self, amount: float, refresh_time=0.0):
        self.capacity = amount
        self.quantity = amount
        self.refresh_time = refresh_time
        if self.refresh_time > 0.0:
            self.is_refreshable = True
        else:
            self.is_refreshable = False

    def refill(self):
        self.quantity = self.capacity

    def empty(self):
        if self.quantity > 0:
            return False
        return True

    def set_pos(self, pos: vec2):
        self.pos = pos

    def update(self):
        sz_mod = 1.0 - (0.9 * (self.quantity / self.capacity) + 0.1)
        self.selfSurf = self.partSurfs[int(self.partCount * sz_mod)]
        if self.is_refreshable and self.quantity == 0:
            self.inner_counter += 1
            if (GAME_DELTATIME * self.inner_counter) >= self.refresh_time / GAME_TIME_SCALE:
                self.refill()
                self.inner_counter = 0

    def __str__(self) -> str:
        return self.r_type

    def name(self) -> str:
        return self.r_name

    def draw(self):
        super().draw()
        if self.is_selected:
            self.desc_text.pos = vec2(self.pos.x, self.pos.y - self.dim.y + 4)
            self.desc_text.draw()

    def take(self, amount: float) -> tuple:
        delta = amount
        if self.quantity < amount:
            delta = self.quantity
        self.quantity -= delta
        return self.__str__(), delta


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
        self.frame_size = vec2(16, 16)
        self.inner_counter = 0

    # load animation frames from file
    def load(self, texture: pygame.Surface, row_id=0, frame_size=vec2(16, 16)):
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

    def get_frame(self) -> pygame.Surface:
        return self.anim_surfs[self.cur_frame]

    def add_frame(self, frame=pygame.Surface):
        self.anim_surfs.append(frame)


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

    def __init__(self, win_surface: pygame.Surface = None, pos=vec2(), dim=vec2(), texture=None):
        super().__init__(win_surface=win_surface, pos=pos, dim=dim, texture=texture)

        if texture is not None:
            self.load_textures(texture)

    def load_textures(self, texture: pygame.Surface):
        assert(texture is not None)

        self.anims = dict()

        self.anims["idle_f"] = Animation(1, 0)
        self.anims["idle_f"].load(texture, row_id=0, frame_size=vec2(16, 16))
        self.anims["idle_b"] = Animation(1, 0)
        self.anims["idle_b"].load(texture, row_id=1, frame_size=vec2(16, 16))

        self.anims["walk_f"] = Animation(8, 0.05)
        self.anims["walk_f"].load(texture, row_id=0, frame_size=vec2(16, 16))
        self.anims["walk_b"] = Animation(8, 0.05)
        self.anims["walk_b"].load(texture, row_id=1, frame_size=vec2(16, 16))

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
        self.selfSurf = pygame.transform.scale(self.anims[self.cur_anim].get_frame(), self.dim.data())

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
                    self.wander_at(self.pos + vec2(randfloat(0.5, 1), randfloat(0.5, 1)) * 50)
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
                self.target_pos = (self.wandering_pos + vec2(randfloat(-0.5, 0.5), randfloat(-0.5, 0.5)) * self.wandering_radius)
                self.is_moving = True
                self.is_move_finished = False

    def draw(self):
        super().draw()  # for now

        if self.is_selected:
            if self.is_moving:
                pygame.draw.line(self.targetSurf, G_GREEN, self.pos.data(), self.target_pos.data())
            self.desc_text.pos = vec2(self.pos.x, self.pos.y - self.dim.y + 4)
            self.desc_text.draw()


def sort_peasants_depth(a: Peasant) -> float:
    return a.pos.y


class Camp(Object2D):
    team: int = 0
    res_texts = dict()

    peasants: list = list()
    resource_places: list = list()

    is_selected: bool = False

    # resources
    res_amounts = dict()
    #

    def initialize(self):
        self.res_texts["food"] = Text2D(pos=vec2(2, 4), size=18, win_surface=self.targetSurf)
        self.res_texts["wood"] = Text2D(pos=vec2(2, 24), size=18, win_surface=self.targetSurf)
        self.res_texts["stone"] = Text2D(pos=vec2(2, 44), size=18, win_surface=self.targetSurf)
        self.res_texts["gold"] = Text2D(pos=vec2(2, 64), size=18, win_surface=self.targetSurf)

        self.res_amounts["food"] = 0
        self.res_amounts["wood"] = 0
        self.res_amounts["stone"] = 0
        self.res_amounts["gold"] = 0

        self.update()

    def update(self):
        self.res_texts["food"].text = tr("food").capitalize()+": " + str(self.res_amounts["food"])
        self.res_texts["wood"].text = tr("wood").capitalize()+": " + str(self.res_amounts["wood"])
        self.res_texts["stone"].text = tr("stone").capitalize()+": " + str(self.res_amounts["stone"])
        self.res_texts["gold"].text = tr("gold").capitalize()+": " + str(self.res_amounts["gold"])

        for txt in self.res_texts.values():
            txt.update()

        for rp in self.resource_places:
            rp.update()

        for _p in self.peasants:
            _p.update()

    def selection_event(self, m_pos: vec2):
        if m_pos.in_rect(self.pos - self.dim*0.5, self.pos + self.dim*0.5):
            self.is_selected = True
        else:
            self.is_selected = False
        sel_count: int = 0
        for _p in self.peasants:
            if m_pos.in_rect(_p.pos - _p.dim*0.5, _p.pos + _p.dim*0.5):
                if sel_count < 1:
                    _p.is_selected = True
                    sel_count += 1
            else:
                if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    sel_count = 0
                    _p.is_selected = False
        for _r in self.resource_places:
            if m_pos.in_rect(_r.pos - _r.dim * 0.5, _r.pos + _r.dim * 0.5):
                _r.is_selected = True
            else:
                _r.is_selected = False

    def draw(self):
        super().draw()

        for rp in self.resource_places:
            rp.draw()

        for _p in self.peasants:
            if not _p.is_gathering:
                for r in self.resource_places:
                    if not r.empty() and _p.specialization == r.__str__():
                        _p.gather_at(r)
                        break

        self.peasants.sort(key=sort_peasants_depth)

        for _p in self.peasants:
            _p.draw()
            for rp in self.resource_places:
                if _p.pos.y < rp.pos.y:
                    rp.draw()

        if self.is_selected:
            for _p in self.peasants:
                pygame.draw.line(self.targetSurf, G_RED, self.pos.data(), _p.pos.data(), 2)

            for txt in self.res_texts.values():
                txt.draw()

    def register_resource(self, r: Resource):
        self.resource_places.append(r)

    def attach_peasant(self, p: Peasant):
        p.camp_obj = self
        p.wander_at(self.pos + vec2(100, 100), r=100)
        if p.specialization == "food":
            p.set_name(WOMEN_NAMES[rand(0, len(WOMEN_NAMES) - 1)], gender="girl")
        else:
            p.set_name(MEN_NAMES[rand(0, len(MEN_NAMES)-1)])
        self.peasants.append(p)
#


def get_resource_copy(r_id: int) -> Resource:
    if GAME_RESOURCES.__len__() == 0:
        print("No resources loaded!")
        exit(-2)
    if GAME_RESOURCES.__len__() < r_id:
        print("Resource out of bounds ID!")
        exit(-1)
    return copy.copy(GAME_RESOURCES[r_id])


def get_peasant_copy(spec: str) -> Peasant:
    if GAME_PEASANTS.__len__() == 0:
        print("No peasants loaded!")
        exit(-2)
    if spec not in GAME_PEASANTS.keys():
        print("Peasant spec not found!")
        exit(-1)
    pc = GAME_PEASANTS[spec].__len__()
    return copy.copy(GAME_PEASANTS[spec][rand(0, pc-1)])


def load_tex(fname=str()) -> pygame.Surface:
    tex: pygame.Surface
    try:
        tex = pygame.image.load(fname)
    except pygame.error:
        tex = pygame.Surface((16, 16))
    return tex


def load_resource_file(fname: str, scr_surf: pygame.Surface):
    GAME_RESOURCES.clear()
    fp = open(fname, "r")
    fdata = ''.join(fp.readlines())
    for resource in yaml.load(fdata, Loader=yaml.FullLoader):
        r = Resource(dim=vec2(32, 32), win_surface=scr_surf)
        r.set_res(GAME_RESOURCES.__len__(), resource['name'], resource['type'])
        r.is_refreshable = resource['refreshable']
        if r.is_refreshable:
            r.refresh_time = resource['refresh_time']
        # r.hardness = resource['hardness']
        tex = pygame.image.load(resource['texture'])
        r.load_parts(tex, resource['frame_count'])
        GAME_RESOURCES.append(r)


def load_peasants_file(fname: str, scr_surf: pygame.Surface):
    GAME_PEASANTS.clear()
    fp = open(fname, "r")
    fdata = ''.join(fp.readlines())
    for peasant in yaml.load(fdata, Loader=yaml.FullLoader):
        p = Peasant(dim=vec2(32, 32), win_surface=scr_surf)

        p.gender = peasant['gender']
        p.specialization = peasant['spec']

        tex = pygame.image.load(peasant['texture'])
        p.load_textures(tex)

        if p.specialization not in GAME_PEASANTS.keys():
            GAME_PEASANTS[p.specialization] = list()
        GAME_PEASANTS[p.specialization].append(p)


pygame.init()
dPtr = pygame.display   # display pointer
scrSurf = dPtr.set_mode((GAME_WIDTH, GAME_HEIGHT))
dPtr.set_caption(GAME_TITLE)
#

game_objs = list()
m_quit = False

load_resource_file("cfg/res.yml", scrSurf)
load_peasants_file("cfg/pss.yml", scrSurf)

# fill object array
mainCamp = Camp(pos=vec2(250, 100), dim=vec2(96, 96), win_surface=scrSurf, texture=load_tex("img/camp_0.png"))
mainCamp.initialize()

if True:
    for a in range(0, 2):
        p = get_peasant_copy("food")
        p.assign("food", 0.5, 3)
        p.pos = vec2(200 + 50*a**2, 50 + 50*a**2)
        mainCamp.attach_peasant(p)

    for a in range(0, 2):
        p = get_peasant_copy("wood")
        p.assign("wood", 1.8, 2)
        p.pos = vec2(200+50*a**2, 50 + 50*a**2)
        mainCamp.attach_peasant(p)

    for a in range(0, 2):
        p = get_peasant_copy("stone")
        p.assign("stone", 3, 1)
        p.pos = vec2(200+50*a**2, 50 + 50*a**2)
        mainCamp.attach_peasant(p)


game_objs.append(mainCamp)
#
resPlace = 0


def place_res(ev: pygame.event):
    global resPlace
    if ev.button == pygame.BUTTON_RIGHT:
        res = get_resource_copy(resPlace)
        res.set_pos(vec2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))
        if resPlace == 1 or resPlace == 0:
            res.fill(50, refresh_time=60 + 120 * randfloat(0, 1))
        else:
            res.fill(100)
        mainCamp.register_resource(res)
    elif ev.button == pygame.BUTTON_WHEELUP:
        if resPlace < (GAME_RESOURCES.__len__() - 1):
            resPlace += 1
    elif ev.button == pygame.BUTTON_WHEELDOWN:
        if resPlace >= 1:
            resPlace -= 1


def quit_event(ev: pygame.event):
    global m_quit
    m_quit = True


def select_event(ev: pygame.event):
    global mainCamp
    if ev.button == pygame.BUTTON_LEFT:
        mainCamp.selection_event(vec2(ev.pos[0], ev.pos[1]))


def game_speed_fast(ev: pygame.event):
    global GAME_TIME_SCALE
    GAME_TIME_SCALE = 5.0


def game_speed_normal(ev: pygame.event):
    global GAME_TIME_SCALE
    GAME_TIME_SCALE = 1.0


eproc = event_processor()
eproc.bind(pygame.QUIT, quit_event)
eproc.bind_keydown(pygame.K_ESCAPE, quit_event)
eproc.bind(pygame.MOUSEBUTTONDOWN, place_res)
eproc.bind(pygame.MOUSEBUTTONDOWN, select_event)
eproc.bind_keydown(pygame.K_SPACE, game_speed_fast)
eproc.bind_keyup(pygame.K_SPACE, game_speed_normal)

clock = pygame.time.Clock()
while not m_quit:
    eproc.update()

    scrSurf.fill((0x72, 0x94, 0x4F))
    for obj in game_objs:
        obj.update()
        obj.draw()

    dPtr.update()
    clock.tick(GAME_TFPS)
pygame.quit()