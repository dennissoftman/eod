#!/usr/bin/python3
# encoding: utf-8

import yaml
import copy
import noise

from eod_events import *
from eod_resources import *
from eod_peasants import *
from eod_structures import *


# class ParticleEffect:
#     color: icolor
#     target_surf: pygame.Surface
#     particle_count: int
#     lifetime: float
#     time_alive: float = 0.0
#
#     pos: vec2
#
#     # def a(p: vec2, p_id: int, t: float) -> tuple:
#     # function that returns velocity for particle for time @t
#     pos_func = None
#     # def a(c: icolor, t: float) -> tuple:
#     # function that returns color for particle for time @t
#     color_func = None
#
#     def __init__(self,
#                  pos: vec2 = vec2(),
#                  pcount: int = 1,
#                  ttl: float = 3,
#                  color: icolor = icolor(),
#                  win_surface: pygame.Surface = None,
#                  pos_func=None, col_func=None):
#         self.particle_count = pcount
#         self.lifetime = ttl
#         self.target_surf = win_surface
#         self.color = color
#         self.pos = pos
#         self.pos_func = pos_func
#         self.color_func = col_func
#
#     def update(self):
#         self.time_alive += GAME_DELTATIME * GAME_TIME_SCALE
#
#     def is_alive(self):
#         if self.time_alive <= self.lifetime:
#             return True
#         return False
#
#     def draw(self):
#         for i in range(0, self.particle_count):
#             if self.color_func is not None:
#                 self.color = self.color_func(self.color, self.time_alive)
#             pos: tuple
#             if self.pos_func is not None:
#                 pos = self.pos_func(self.pos, i, self.time_alive)
#             else:
#                 pos = self.pos.data()
#             self.target_surf.fill(self.color.data(), (int(pos[0]) - 1, int(pos[1]) - 1, 2, 2))


def grid_pos(cell=(0, 0), cell_size=(76, 38)) -> tuple:
    return cell_size[0] * cell[0] + (cell_size[0] >> 1) * (cell[1] % 2 - 1), (cell_size[1] >> 1) * (cell[1] - 1)


gresl = resource_loader()
gresl.load_pak("data.pak")
# here you can load additional pak files
# i'll add later config files for data loading

pygame.init()
dPtr = pygame.display   # display pointer
scrSurf = dPtr.set_mode((GAME_WIDTH, GAME_HEIGHT))
dPtr.set_caption(GAME_TITLE)
#

game_objs = list()
m_quit = False


def load_tex(fname=str()) -> pygame.Surface:
    global gresl

    tex: pygame.Surface
    try:
        tex = pygame.image.load_extended(gresl.read_fp(fname))
    except pygame.error:
        print('Failed to load "', fname, '"')
        tex = pygame.Surface((16, 16))
    return tex


def preload_fonts(fonts: dict):
    global gresl
    GAME_FONTS.clear()
    for fn in fonts.keys():
        GAME_FONTS[fn] =\
            pygame.font.Font(gresl.read_fp(fonts[fn]), 16)


def load_resource_file(fname: str, scr_surf: pygame.Surface):
    global gresl

    GAME_RESOURCES.clear()
    fdata = gresl.read(fname).decode('utf-8')

    # for now
    dims = {'food': vec2((24, 24)),
            'wood': vec2((48, 48)),
            'stone': vec2((32, 32))}
    #
    dim: vec2
    for resource in yaml.load(fdata, Loader=yaml.FullLoader):
        if resource['type'] not in dims.keys():
            dim = dims['food']
        else:
            dim = dims[resource['type']]

        r = Resource(dim=dim, win_surface=scr_surf)
        r.set_res(GAME_RESOURCES.__len__(), resource['name'], resource['type'])
        r.is_refreshable = resource['refreshable']
        if r.is_refreshable:
            r.refresh_time = resource['refresh_time']

        # r.hardness = resource['hardness']

        tex = load_tex(resource['texture'])
        r.load_parts(tex, resource['frame_count'])

        if resource['type'] not in GAME_RESOURCES.keys():
            GAME_RESOURCES[resource['type']] = list()
        GAME_RESOURCES[resource['type']].append(r)


def load_peasants_file(fname: str, scr_surf: pygame.Surface):
    global gresl

    GAME_PEASANTS.clear()
    fdata = gresl.read(fname).decode('utf-8')
    for peasant in yaml.load(fdata, Loader=yaml.FullLoader):
        p = Peasant(dim=vec2((32, 32)), win_surface=scr_surf)

        p.gender = peasant['gender']
        p.specialization = peasant['spec']

        tex = load_tex(peasant['texture'])
        p.load_textures(tex)

        if p.specialization not in GAME_PEASANTS.keys():
            GAME_PEASANTS[p.specialization] = list()
        GAME_PEASANTS[p.specialization].append(p)


preload_fonts({"serif": "/font/uni_times.ttf"})
load_resource_file("/cfg/res.yml", scrSurf)
load_peasants_file("/cfg/pss.yml", scrSurf)

# fill object array
mainCamp = Camp(pos=vec2(grid_pos((3, 5))), dim=vec2((128, 128)), win_surface=scrSurf, texture=load_tex("/img/camp_0.png"))
mainCamp.initialize()

if True:
    # spawn food resources
    for i in range(0, rand(10, 40)):
        res = get_resource_copy("food", -1)
        x, y = randfloat(-200, 200), randfloat(-200, 200)
        res.set_pos(vec2((600 + x*0.2 - y*0.5, 400 + y*1.2)))
        res.fill(50, refresh_time=60 + 120 * randfloat(0, 1))
        mainCamp.register_resource(res)

    for i in range(0, rand(10, 25)):
        res = get_resource_copy("wood", -1)
        x, y = randfloat(-200, 200), randfloat(-200, 200)
        res.set_pos(vec2((800 + x*0.3 - y*0.4 + 5*i*randfloat(-1, 1), 400 + y)))
        res.fill(50, refresh_time=60 + 120 * randfloat(0, 1))
        mainCamp.register_resource(res)

    for i in range(0, rand(5, 10)):
        res = get_resource_copy("stone", -1)
        x, y = randfloat(-100, 100), randfloat(-100, 100)
        res.set_pos(vec2((200 + x, 400 + y - x * 0.2)))
        res.fill(100)
        mainCamp.register_resource(res)


if True:
    for a in range(0, 2):
        p = get_peasant_copy("food")
        p.assign("food", 0.5, 3)
        p.pos = vec2((200 + 50*a**2, 50 + 50*a**2))
        mainCamp.attach_peasant(p)

    for a in range(0, 2):
        p = get_peasant_copy("wood")
        p.assign("wood", 1.8, 2)
        p.pos = vec2((200+50*a**2, 50 + 50*a**2))
        mainCamp.attach_peasant(p)

    for a in range(0, 2):
        p = get_peasant_copy("stone")
        p.assign("stone", 3, 1)
        p.pos = vec2((200+50*a**2, 50 + 50*a**2))
        mainCamp.attach_peasant(p)


game_objs.append(mainCamp)
#
resPlace = 0


def quit_event(ev: pygame.event):
    global m_quit
    m_quit = True


def select_event(ev: pygame.event):
    global mainCamp
    if ev.button == pygame.BUTTON_LEFT:
        mainCamp.selection_event(vec2((ev.pos[0], ev.pos[1])))


def game_speed_fast(ev: pyevent):
    global GAME_TIME_SCALE
    GAME_TIME_SCALE = 5.0


def game_speed_normal(ev: pyevent):
    global GAME_TIME_SCALE
    GAME_TIME_SCALE = 1.0


eproc = event_processor()
eproc.bind(pygame.QUIT, quit_event)
eproc.bind_keydown(pygame.K_ESCAPE, quit_event)
# eproc.bind(pygame.MOUSEBUTTONDOWN, place_res)
eproc.bind(pygame.MOUSEBUTTONDOWN, select_event)
eproc.bind_keydown(pygame.K_SPACE, game_speed_fast)
eproc.bind_keyup(pygame.K_SPACE, game_speed_normal)

#
grass_texs: list = list()
grass_width: int = 76
grass_height: int = 38
for i in range(0, 3):
    grass_texs.append(pygame.transform.scale(load_tex("/img/grass_{0}.png".format(i)), (grass_width, grass_height)))
#

# Background rendering
bgSurf = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
for i in range(0, 39):
    for j in range(0, 18):
        # get simplex noise
        grass_density = noise.snoise2(i, j)
        # move to positive half
        grass_density = (grass_density + 1.0)/2.0
        # calculate grass density id
        grass_id = int(grass_density * grass_texs.__len__()) % grass_texs.__len__()

        bgSurf.blit(pygame.transform.flip(grass_texs[grass_id],
                                          noise.snoise2(j, i) > 0, noise.pnoise2(i, j) > 0),
                    grid_pos((j, i), (grass_width, grass_height)))
#

# # performance analyzing
# import time
# from matplotlib import pyplot as plt
# frame_times = list()
# t0: float = 0.0
# #

clock = pygame.time.Clock()
while not m_quit:
    eproc.update()

    # Draw background
    scrSurf.blit(bgSurf, (0, 0))
    #

    for obj in game_objs:
        obj.update()
        obj.draw()

    # for peff in peff_list:
    #     if not peff.is_alive():
    #         peff_list.remove(peff)
    #         continue
    #     peff.update()
    #     peff.draw()

    dPtr.update()
    clock.tick(GAME_TFPS)
    # # performance analyzing
    # if t0 != 0.0:
    #     t = (time.time()*1000) - t0
    #     frame_times.append(round(t))
    # t0 = time.time() * 1000
    # #
pygame.quit()

# # performance analyzing
# plt.plot(frame_times)
# plt.ylabel("frame time (ms)")
# plt.xlabel("frame")
# plt.show()
# #
