# encoding: utf-8

import pygame


class event_processor:
    GAME_EVENTS = dict()
    GAME_KEYDOWN_EVENTS = dict()
    GAME_KEYUP_EVENTS = dict()

    def bind(self, ev, func):
        if ev not in self.GAME_EVENTS.keys():
            self.GAME_EVENTS[ev] = list()
        self.GAME_EVENTS[ev].append(func)

    def bind_keydown(self, key, func):
        if key not in self.GAME_EVENTS.keys():
            self.GAME_KEYDOWN_EVENTS[key] = list()
        self.GAME_KEYDOWN_EVENTS[key].append(func)

    def bind_keyup(self, key, func):
        if key not in self.GAME_EVENTS.keys():
            self.GAME_KEYUP_EVENTS[key] = list()
        self.GAME_KEYUP_EVENTS[key].append(func)

    def unbind(self, ev, func):
        if ev in self.GAME_EVENTS.keys():
            self.GAME_EVENTS[ev].remove(func)

    def unbind_key(self, key, func):
        if key in self.GAME_KEYDOWN_EVENTS.keys():
            self.GAME_KEYDOWN_EVENTS[key].remove(func)

    def update(self):
        for ev in pygame.event.get():
            if ev.type in self.GAME_EVENTS.keys():
                for ev_exec in self.GAME_EVENTS[ev.type]:
                    ev_exec(ev)
            elif ev.type == pygame.KEYDOWN:
                if ev.key in self.GAME_KEYDOWN_EVENTS.keys():
                    for ev_kexec in self.GAME_KEYDOWN_EVENTS[ev.key]:
                        ev_kexec(ev)
            elif ev.type == pygame.KEYUP:
                if ev.key in self.GAME_KEYUP_EVENTS.keys():
                    for ev_kexec in self.GAME_KEYUP_EVENTS[ev.key]:
                        ev_kexec(ev)