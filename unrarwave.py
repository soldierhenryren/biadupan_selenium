from pathlib import Path

from numpy import arange
import os
import tarfile

# 目录整理
class DirPathThing:
    def __init__(self, path):
        self.path = path / 'data_aishell'
        pass

    def word2path(self, word):
        # BAC009S0002W0469  to path/'wav/S0002.tar.gz'
        name = word[6, 12] + '.tar.gz'
        file_path = self.path / 'wav' / name
        return file_path

    # 整理文件夹
    def condition(self):
        source_path = self.path / 'wav'
        file_list = os.listdir(source_path)
        # 进行解压
        for i in arange(len(file_list)):
            file = file_list[i]
            file_path = os.path.join(source_path, file)
            if tarfile.is_tarfile(file_path):
                with tarfile.open(file_path) as tf:
                    try:
                        tf.extractall(source_path)
                    except tarfile.ReadError:
                        print('出现异常')
                    print('{}已经完成'.format(i))

    def excute(self):
        self.condition()
        pass


path = Path('/Volumes/seagate/usefule')
dirpaththing = DirPathThing(path)
dirpaththing.excute()