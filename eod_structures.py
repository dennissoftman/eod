# encoding: utf-8

import pygame
from eod_peasants import *

from eod_men_names import *
from eod_women_names import *


class Structure(Object2D):
    # s_stype is structure type, available types:
    #   none  - structure just for fun! no sense
    #   camp  - main building, some kind of town hall. Any building with roof and walls can be camp
    #   house - space for peasants to live
    #   production:id - some kind of structure for resource[id] production (lumberjack house, quarry, etc.)
    #   processing:id_in:id_out - some kind of structure for resource[id] processing (sawmill, kitchen, etc.)
    #   entertainment:id - some kind of structure for peasant entertainment[id] (church, circus, pub)
    #
    s_type: str = "none"
    s_owners: list = list()

    def add_peasant(self, other: Peasant):
        self.s_owners.append(other)

    def is_owner(self, other: Peasant) -> bool:
        if other in self.s_owners:
            return True
        return False


class House(Structure):

    def initialize(self):
        self.s_type = "house"


class Camp(Structure):
    team: int = 0
    res_texts = dict()

    peasants: list = list()
    resource_places: list = list()
    structures: list = list()

    is_selected: bool = False

    # resources
    res_amounts = dict()
    #

    def initialize(self):
        self.s_type = "camp"

        self.res_texts["food"] = Text2D(pos=vec2((2, 4)), size=18, win_surface=self.targetSurf)
        self.res_texts["wood"] = Text2D(pos=vec2((2, 24)), size=18, win_surface=self.targetSurf)
        self.res_texts["stone"] = Text2D(pos=vec2((2, 44)), size=18, win_surface=self.targetSurf)
        self.res_texts["gold"] = Text2D(pos=vec2((2, 64)), size=18, win_surface=self.targetSurf)

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
                if sel_count < 1:
                    _r.is_selected = True
                    sel_count += 1
            else:
                _r.is_selected = False
        for _s in self.structures:
            if m_pos.in_rect(_s.pos - _s.dim * 0.5, _s.pos + _s.dim * 0.5):
                if sel_count < 1:
                    _s.is_selected = True
                    sel_count += 1
            else:
                _s.is_selected = False

    def draw(self):
        super().draw()

        for _s in self.structures:
            _s.draw()

        for rp in self.resource_places:
            rp.draw()

        for _p in self.peasants:
            if not _p.is_gathering:
                for r in self.resource_places:
                    if not r.empty() and _p.specialization == r.__str__():
                        _p.gather_at(r)
                        break

        self.peasants.sort(key=peasant_get_depth_sort)

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
        p.wander_at(self.pos + vec2((100, 100)), r=100)
        if p.specialization == "food":
            p.set_name(WOMEN_NAMES[rand(0, len(WOMEN_NAMES) - 1)], gender="girl")
        else:
            p.set_name(MEN_NAMES[rand(0, len(MEN_NAMES)-1)])
        self.peasants.append(p)