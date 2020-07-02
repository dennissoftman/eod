import pygame
from enum import Enum
from random import randint as rand
from random import uniform as randfloat

# global vars
GAME_TITLE = "Evolve or die"
GAME_WIDTH = 1280
GAME_HEIGHT = 720
GAME_TFPS = 30
GAME_DELTATIME = 1./GAME_TFPS
GAME_TIME_SCALE = 1.
GAME_RENDERMODE = 1     # 1 - textured, 0 - colored rects
GAME_LANG = "ru"

G_BLACK = (0x00, 0x00, 0x00)
G_RED = (0xFF, 0x00, 0x00)
G_GREEN = (0x00, 0xFF, 0x00)
G_BLUE = (0x00, 0x00, 0xFF)
G_WHITE = (0xFF, 0xFF, 0xFF)

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

TR_ENGLISH = {}
TR_RUSSIAN = {"food": "еда", "wood": "дерево", "stone": "камни", "gold": "золото",
              "foodman": "знахарь", "woodman": "дровосек", "stoneman": "каменщик", "goldman": "золотодобытчик",
              "foodgirl": "знахарка", "woodgirl": "дровосечиха", "stonegirl": "каменщица", "goldgirl": "золотодобытчица",
              "aaron": "артем", "andrew": "андрей", "abel": "абель", "adrian": "адриан", "arnold": "алексей", "alfred": "альфред",
              "ben": "борис", "bill": "богдан", "bert": "ваня", "bradley": "бредли",
              "chuck": "чук", "caleb": "калеб", "calvin": "коля", "casey": "клим", "christian": "кристиан",
              "dennis": "денис", "daniel": "даниил", "donald": "дональд", "douglas": "дуглас", "doyle": "дойль"}

#


def tr(key: str = str()):
    if GAME_LANG == "ru":
        if key not in TR_RUSSIAN.keys():
            return key
        return TR_RUSSIAN[key]
    if key not in TR_ENGLISH.keys():
        return key
    return TR_ENGLISH[key]


class vec2:
    x: float
    y: float

    def __init__(self, x=0., y=0.):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __mul__(self, other: float):
        return vec2(self.x*other, self.y*other)

    def __idiv__(self, other: float):
        if other != 0.:
            self.x /= other
            self.y /= other
        return self

    def __imul__(self, other: float):
        self.x *= other
        self.y *= other
        return self

    def __abs__(self):
        return vec2(abs(self.x), abs(self.y))

    def __round__(self, n=None):
        return vec2(round(self.x), round(self.y))

    def __len__(self):
        return (self.x * self.x + self.y * self.y)**0.5

    def __le__(self, other):
        if self.x <= other.x and self.y <= other.y:
            return True
        return False

    def normalized(self):
        if self.__len__() == 0:
            return vec2(0, 0)
        return vec2(self.x, self.y) * (1. / self.__len__())

    def in_rect(self, top_left, bot_right) -> bool:
        return (top_left.x <= self.x <= bot_right.x) and (top_left.y <= self.y <= bot_right.y)

    # helper function for pygame.draw
    def data(self) -> tuple:
        return round(self.x), round(self.y)


class icolor:
    r: int
    g: int
    b: int

    def __init__(self, val: tuple = (0, 0, 0)):
        self.r = val[0]
        self.g = val[1]
        self.b = val[2]

    def data(self) -> tuple:
        return self.r, self.g, self.b


class Object2D:
    pos: vec2
    dim: vec2
    selfSurf: pygame.Surface = None
    targetSurf: pygame.Surface

    color: icolor

    def __init__(self, win_surface: pygame.Surface = None,
                 pos=vec2(), dim=vec2(),
                 color=icolor(), texture: pygame.Surface = None):
        self.targetSurf = win_surface
        self.pos = pos
        self.dim = dim
        if texture is None:
            self.selfSurf = pygame.Surface(self.dim.data())
        else:
            self.selfSurf = pygame.transform.scale(texture, self.dim.data())
        colors = dict()
        for y in range(0, int(self.dim.y)):
            for x in range(0, int(self.dim.x)):
                col = self.selfSurf.get_at((x, y))[:3]
                if col == G_BLACK:
                    continue
                if col not in colors.keys():
                    colors[col] = 1
                else:
                    colors[col] += 1
        maxc = 0
        for col in colors.keys():
            if colors[col] > maxc:
                maxc = colors[col]
                self.color = icolor(col)

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
        self.target_surf.blit(self.text_surf, (self.pos.x, self.pos.y))


# game-related classes
WANDER_SPEED = 40
MOVE_SPEED = 100


class ResID(Enum):
    NONE = 0
    FOOD = 1
    WOOD = 2
    STONE = 3
    GOLD = 4


class Resource(Object2D):
    r_id: ResID
    capacity: float = 0
    quantity: float = 0
    partSurfs: list
    is_refreshable: bool = False
    refresh_time: float = 0.0

    inner_counter: int = 0

    def __init__(self, win_surface: pygame.Surface = None,
                 pos=vec2(), dim=vec2(),
                 color=icolor(), texture: pygame.Surface = None):
        super().__init__(win_surface=win_surface, pos=pos, dim=dim, color=color, texture=texture)
        if texture is None:
            return
        self.partSurfs = list()
        tex_dim: vec2 = vec2(texture.get_size()[0]//5, texture.get_size()[1])
        for i in range(0, 5):
            tex = texture.subsurface((int(tex_dim.x)*i, 0, int(tex_dim.x), int(tex_dim.y)))
            self.partSurfs.append(pygame.transform.scale(tex, dim.data()))

    def fill(self, r_id: ResID, amount: float, refresh_time=0.0):
        self.r_id = r_id
        self.capacity = amount
        self.quantity = amount
        self.refresh_time = refresh_time
        if self.refresh_time > 0.0:
            self.is_refreshable = True
        else:
            self.is_refreshable = False

        if r_id == ResID.FOOD:
            self.color = icolor((0xA3, 0x00, 0x39))
        elif r_id == ResID.WOOD:
            self.color = icolor((0x6E, 0x3E, 0x0E))
        elif r_id == ResID.STONE:
            self.color = icolor((0x8F, 0x8F, 0x8F))
        elif r_id == ResID.GOLD:
            self.color = icolor((0xFC, 0xCD, 0x00))

    def refill(self):
        self.quantity = self.capacity

    def empty(self):
        if self.quantity > 0:
            return False
        return True

    def update(self):
        if self.is_refreshable and self.quantity == 0:
            self.inner_counter += 1
            if (GAME_DELTATIME * self.inner_counter) >= self.refresh_time / GAME_TIME_SCALE:
                self.refill()
                self.inner_counter = 0

    def __str__(self) -> str:
        if self.r_id == ResID.FOOD:
            return "food"
        elif self.r_id == ResID.WOOD:
            return "wood"
        elif self.r_id == ResID.STONE:
            return "stone"
        elif self.r_id == ResID.GOLD:
            return "gold"
        return str()

    def draw(self):
        sz_mod = (self.quantity / self.capacity) * 1.2
        if sz_mod >= 0.8:
            self.selfSurf = self.partSurfs[0]
        elif 0.75 <= sz_mod < 0.8:
            self.selfSurf = self.partSurfs[1]
        elif 0.4 <= sz_mod < 0.75:
            self.selfSurf = self.partSurfs[2]
        elif 0.1 <= sz_mod < 0.4:
            self.selfSurf = self.partSurfs[3]
        else:
            self.selfSurf = self.partSurfs[4]
        super().draw()

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
    descText: Text2D

    def __init__(self, win_surface: pygame.Surface = None, pos=vec2(), dim=vec2(), color=icolor(), texture=None):
        super().__init__(win_surface=win_surface, pos=pos, dim=dim, color=color, texture=texture)

        self.descText = Text2D(win_surface=win_surface, size=16)

        self.anims = dict()
        if texture is None:
            return

        self.anims["idle_f"] = Animation(1, 0)
        self.anims["idle_f"].load(texture, row_id=0, frame_size=vec2(16, 16))
        self.anims["idle_b"] = Animation(1, 0)
        self.anims["idle_b"].load(texture, row_id=1, frame_size=vec2(16, 16))

        self.anims["walk_f"] = Animation(8, 0.05)
        self.anims["walk_f"].load(texture, row_id=0, frame_size=vec2(16, 16))
        self.anims["walk_b"] = Animation(8, 0.05)
        self.anims["walk_b"].load(texture, row_id=1, frame_size=vec2(16, 16))

        self.anims["gather_f"] = Animation(8, 0.05)
        self.anims["gather_f"].load(texture, row_id=2, frame_size=vec2(16, 16))
        self.anims["gather_b"] = Animation(8, 0.05)
        self.anims["gather_b"].load(texture, row_id=2, frame_size=vec2(16, 16))

    def set_name(self, name: str, gender: str = "man"):
        self.name = name
        self.gender = gender
        self.descText.set_text(tr(self.name.lower()).capitalize() + ", " + tr(self.specialization + self.gender))

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
            if self.is_gathering:
                self.cur_anim = "gather"
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
                self.is_moving = False
                if (GAME_DELTATIME * self.inner_counter) >= (self.gather_period / GAME_TIME_SCALE):
                    self.inner_counter = 0
                    self.inventory.append(self.gather_obj.take(self.inventory_capacity))
                    self.target_pos = self.camp_obj.pos
                    self.is_moving = True
                    self.is_move_finished = False
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
            self.descText.pos = vec2(self.pos.x, self.pos.y - self.dim.y + 4)
            self.descText.draw()


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

        pygame.event.get()
        if pygame.mouse.get_pressed()[0]:
            m_pos: vec2 = vec2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
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
                        _p.is_selected = False

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


def load_tex(fname=str()) -> pygame.Surface:
    tex: pygame.Surface
    try:
        tex = pygame.image.load(fname)
    except pygame.error:
        tex = pygame.Surface((16, 16))
    return tex


pygame.init()
dPtr = pygame.display   # display pointer
scrSurf = dPtr.set_mode((GAME_WIDTH, GAME_HEIGHT))
dPtr.set_caption(GAME_TITLE)
#

game_objs = list()
m_quit = False

# fill object array
mainCamp = Camp(pos=vec2(100, 100), dim=vec2(96, 96), win_surface=scrSurf, texture=load_tex("img/camp_0.png"))
mainCamp.initialize()

if True:
    food_p_tex = load_tex("img/foodman_0.png")
    wood_p_tex = load_tex("img/woodman_0.png")
    stone_p_tex = load_tex("img/stoneman_0.png")

    p = Peasant(pos=vec2(200, 50), dim=vec2(32, 32), win_surface=scrSurf, texture=food_p_tex)
    p.assign("food", 0.5, 2)
    mainCamp.attach_peasant(p)

    p = Peasant(pos=vec2(100, 100), dim=vec2(32, 32), win_surface=scrSurf, texture=stone_p_tex)
    p.assign("stone", 1.5, 1)
    mainCamp.attach_peasant(p)
    p = Peasant(pos=vec2(160, 300), dim=vec2(32, 32), win_surface=scrSurf, texture=stone_p_tex)
    p.assign("stone", 1.5, 1)
    mainCamp.attach_peasant(p)
    p = Peasant(pos=vec2(50, 150), dim=vec2(32, 32), win_surface=scrSurf, texture=stone_p_tex)
    p.assign("stone", 1.5, 1)
    mainCamp.attach_peasant(p)

    p = Peasant(pos=vec2(150, 200), dim=vec2(32, 32), win_surface=scrSurf, texture=wood_p_tex)
    p.assign("wood", 1, 1)
    mainCamp.attach_peasant(p)
    p = Peasant(pos=vec2(100, 100), dim=vec2(32, 32), win_surface=scrSurf, texture=wood_p_tex)
    p.assign("wood", 1, 1)
    mainCamp.attach_peasant(p)
    p = Peasant(pos=vec2(200, 350), dim=vec2(32, 32), win_surface=scrSurf, texture=wood_p_tex)
    p.assign("wood", 1, 1)
    mainCamp.attach_peasant(p)

game_objs.append(mainCamp)
#

resPlace = ResID.WOOD

clock = pygame.time.Clock()
while not m_quit:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            m_quit = True
            break
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == pygame.BUTTON_RIGHT:
                res_tex = pygame.Surface((16, 16))
                res_dim = vec2(32, 32)
                if resPlace == ResID.FOOD:
                    res_tex = load_tex("img/berries_{:d}.png".format(rand(0, 2)))
                elif resPlace == ResID.WOOD:
                    res_tex = load_tex("img/tree_{:d}.png".format(rand(0, 1)))
                    res_dim = vec2(48, 48)
                elif resPlace == ResID.STONE:
                    res_tex = load_tex("img/rock_{:d}.png".format(rand(0, 1)))
                elif resPlace == ResID.GOLD:
                    res_tex = load_tex("img/gold_ore_0.png")
                res = Resource(pos=vec2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]),
                               dim=res_dim,
                               win_surface=scrSurf,
                               texture=res_tex)

                if resPlace == ResID.WOOD or resPlace == ResID.FOOD:
                    res.fill(resPlace, 50, refresh_time=60 + 120 * randfloat(0, 1))
                else:
                    res.fill(resPlace, 100)
                mainCamp.register_resource(res)
            elif ev.button == pygame.BUTTON_WHEELUP:
                if resPlace.value < 4:
                    resPlace = ResID(resPlace.value + 1)
            elif ev.button == pygame.BUTTON_WHEELDOWN:
                if resPlace.value > 1:
                    resPlace = ResID(resPlace.value - 1)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                m_quit = True
                break
            if ev.key == pygame.K_SPACE:
                GAME_TIME_SCALE = 5.0
            elif ev.key == pygame.K_F5:
                GAME_RENDERMODE = not GAME_RENDERMODE
        elif ev.type == pygame.KEYUP:
            if ev.key == pygame.K_SPACE:
                GAME_TIME_SCALE = 1.0

    scrSurf.fill((0x72, 0x94, 0x4F))
    for obj in game_objs:
        obj.update()
        obj.draw()

    dPtr.update()
    clock.tick(GAME_TFPS)
