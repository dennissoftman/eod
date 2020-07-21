# encoding: utf-8

import tarfile
import zlib
import io
import os

from eod_config import *
import copy

from eod_peasants import Peasant
from eod_basicclasses import Resource


class resource_loader:
    # resources: dict[str, bytes]
    resources: dict

    def __init__(self):
        self.resources = dict()

    def load_pak(self, resfile='data.pak'):
        fp = open(resfile, 'rb')
        pak_data = fp.read()
        fp.close()
        tar_data = zlib.decompress(pak_data)
        tar_file = io.BytesIO(tar_data)

        tar = tarfile.open(fileobj=tar_file, mode='r')

        for tf in tar.getmembers():
            tf_data: tarfile.ExFileObject = tar.extractfile(tf)
            if tf_data is None:
                continue
            npath = os.path.normpath('/' + tf.name)
            print('Loaded "{0}"'.format(npath))
            self.resources[npath] = tf_data.read()

    def read(self, fname='.') -> bytes:
        if fname == '.':
            return bytes()
        if fname not in self.resources.keys():
            print('No preloaded data found: "{0}"'.format(fname))
            return bytes()
        return self.resources[fname]

    def read_fp(self, fname='.'):
        return io.BytesIO(self.read(fname))


def get_resource_copy(r_type: str, r_v: int = 0) -> Resource:
    if GAME_RESOURCES.__len__() == 0:
        print("No resources loaded!")
        exit(-2)
    if r_type not in GAME_RESOURCES.keys():
        print('Resource "{0}" not found!'.format(r_type))
        exit(-1)
    if r_v < 0:
        r_v = rand(0, GAME_RESOURCES[r_type].__len__() - 1)
    r_v %= GAME_RESOURCES[r_type].__len__()
    return copy.copy(GAME_RESOURCES[r_type][r_v])


def get_peasant_copy(spec: str) -> Peasant:
    if GAME_PEASANTS.__len__() == 0:
        print("No peasants loaded!")
        exit(-2)
    if spec not in GAME_PEASANTS.keys():
        print("Peasant spec not found!")
        exit(-1)
    pc = GAME_PEASANTS[spec].__len__()
    return copy.copy(GAME_PEASANTS[spec][rand(0, pc-1)])