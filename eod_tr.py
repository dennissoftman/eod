# encoding: utf-8

from eod_config import GAME_LANG


TR_ENGLISH = {}
TR_RUSSIAN = {"food": "еда", "wood": "дерево", "stone": "камни", "gold": "золото",
              "berries": "ягоды", "oak": "дуб", "birch": "берёза", "rock": "камень", "gold_ore": "золотая руда",
              "blueberry": "голубика", "currant_red": "красная смородина", "currant_blue": "черная смородина",
              "foodman": "знахарь", "woodman": "дровосек", "stoneman": "каменщик", "goldman": "золотодобытчик",
              "foodgirl": "знахарка", "woodgirl": "дровосечиха", "stonegirl": "каменщица", "goldgirl": "золотодобытчица",
              "aaron": "артем", "andrew": "андрей", "abel": "абель", "adrian": "адриан", "arnold": "алексей", "alfred": "альфред",
              "ben": "борис", "bill": "богдан", "bert": "ваня", "bradley": "бредли",
              "chuck": "чук", "caleb": "калеб", "calvin": "коля", "casey": "клим", "christian": "кристиан",
              "dennis": "денис", "daniel": "даниил", "donald": "дональд", "douglas": "дуглас", "doyle": "дойль"}


def tr(key: str = str()):
    if GAME_LANG == "ru":
        if key not in TR_RUSSIAN.keys():
            return key
        return TR_RUSSIAN[key]
    if key not in TR_ENGLISH.keys():
        return key
    return TR_ENGLISH[key]