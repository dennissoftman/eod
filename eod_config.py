# encoding: utf-8

from random import randint as rand
from random import uniform as randfloat

# global config vars
GAME_TITLE = "Evolve or die"
GAME_WIDTH = 1280
GAME_HEIGHT = 720
GAME_TFPS = 60
GAME_DELTATIME = 1./GAME_TFPS
GAME_TIME_SCALE = 1.
GAME_RENDERMODE = 1     # 1 - textured, 0 - colored rects
GAME_LANG = "ru"

GAME_FONTS = dict()

# wood, food, stone, etc. presets (for copying)
GAME_RESOURCES = dict()
# preloaded unit presets (for copying)
GAME_PEASANTS = dict()

# constants

WANDER_SPEED = 40
MOVE_SPEED = 100

G_BLACK = (0x00, 0x00, 0x00)
G_RED = (0xFF, 0x00, 0x00)
G_GREEN = (0x00, 0xFF, 0x00)
G_BLUE = (0x00, 0x00, 0xFF)
G_WHITE = (0xFF, 0xFF, 0xFF)
