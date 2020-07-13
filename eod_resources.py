# encoding: utf-8

import tarfile
import zlib
import io
import os


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
