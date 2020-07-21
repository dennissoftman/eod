# encoding: utf-8

from pygame import Surface
from pygame.transform import scale as pyscale
from pygame import draw as pyrender

from eod_primitives import vec2, icolor
from eod_config import *
from eod_tr import tr


class Object2D:
    pos: vec2
    dim: vec2
    selfSurf: Surface = None
    targetSurf: Surface

    color: icolor

    def __init__(self, win_surface: Surface = None,
                 pos=vec2(), dim=vec2(),
                 texture: Surface = None):
        self.targetSurf = win_surface
        self.pos = pos
        self.dim = dim
        if texture is None:
            self.selfSurf = Surface(self.dim.data())
        else:
            self.selfSurf = pyscale(texture, self.dim.data())

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
            pyrender.rect(self.targetSurf,
                          self.color.data(),
                          (round(self.pos.x - self.dim.x*0.5), round(self.pos.y-self.dim.y*0.5),
                           round(self.dim.x), round(self.dim.y)))


class Text2D:
    pos: vec2
    size: int
    text: str
    color: icolor
    target_surf: Surface
    text_surf: Surface

    def __init__(self, win_surface: Surface = None, pos=vec2(), size=16, text=str()):
        self.pos = pos
        self.size = size
        self.text = text
        self.target_surf = win_surface
        self.color = icolor((0, 0, 0))

    def set_text(self, text: str = str()):
        self.text = text
        self.update()

    def update(self):
        font = GAME_FONTS["serif"]
        self.text_surf = font.render(self.text, False, self.color.data())

    def draw(self):
        self.target_surf.blit(self.text_surf, self.pos.data())


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

    def __init__(self, win_surface: Surface = None,
                 pos=vec2(), dim=vec2(),
                 texture: Surface = None):
        super().__init__(win_surface=win_surface, pos=pos, dim=dim, texture=texture)
        self.desc_text = Text2D(win_surface=self.targetSurf, size=16)

    def set_res(self, r_id, r_name, r_type):
        self.r_id = r_id
        self.r_name = r_name
        self.r_type = r_type

        self.desc_text.set_text(tr(self.r_name))
        self.desc_text.update()

    def load_parts(self, texture: Surface, count: int):
        assert(count > 0)
        self.partCount = count
        self.partSurfs = list()
        tex_dim: vec2 = vec2((texture.get_size()[0] // self.partCount, texture.get_size()[1]))
        for i in range(0, self.partCount):
            tex = texture.subsurface((int(tex_dim.x) * i, 0, int(tex_dim.x), int(tex_dim.y)))
            self.partSurfs.append(pyscale(tex, self.dim.data()))

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
            self.desc_text.pos = vec2((self.pos.x, self.pos.y - self.dim.y + 4))
            self.desc_text.draw()

    def take(self, amount: float) -> tuple:
        delta = amount
        if self.quantity < amount:
            delta = self.quantity
        self.quantity -= delta
        return self.__str__(), delta
