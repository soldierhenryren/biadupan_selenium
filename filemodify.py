# coding=utf-8
import glob
from os import DirEntry, scandir, path, stat

from pathlib import Path
# 后面不要加斜杠
pathstr = '/Volumes/seagate/BEAUTYLEG/89'

pathname = glob.escape(pathstr)
print(pathname)
# 图像文件夹
Path(pathname).joinpath('p').mkdir(mode=0o755, exist_ok=True)
i = 0
for filepath in glob.iglob(pathname + '/**/*.[jJpPBb][pPnNMm][PpgG]', recursive=True):
    source_path = Path(filepath)
    print(filepath)
    i += 1
    source_suffix = source_path.suffix
    path_target = Path(pathname) / 'p'/ (pathstr[-2:]+str(i) + source_suffix)
    source_path.rename(path_target)
    print(path_target)

i = 0
for filepath in glob.iglob(pathname + '/**/*.[rR][Mm]', recursive=True):
    print(filepath)
    # try:
    #     drs =  scandir(filepath)
    #     # 没有报错,但是是目录
    #     suffix = Path(filepath).suffix
    #     tfilepath = filepath[:-len(suffix)]
    #     Path(filepath).rename(tfilepath)
    #     print(tfilepath)
    #     continue
    # except NotADirectoryError :
    #     print('not dir')
    source_path = Path(filepath)
    print('ori',filepath)
    i += 1
    source_suffix = source_path.suffix
    print('str',pathstr)
    # 取目录的后两子为名称
    path_target = Path(pathname) / (pathstr[-2:]+str(i) + source_suffix)
    source_path.rename(path_target)
    print(path_target)

for filepath in glob.iglob(pathname + '/**/*.[3AaMmWwFfrR][GgVvPpMmOoLlKktTpPsS][PpIi4VvsSgGsF]*', recursive=True):
    print(filepath)
    # try:
    #     drs =  scandir(filepath)
    #     # 没有报错,但是是目录
    #     suffix = Path(filepath).suffix
    #     tfilepath = filepath[:-len(suffix)]
    #     Path(filepath).rename(tfilepath)
    #     print(tfilepath)
    #     continue
    # except NotADirectoryError :
    #     print('not dir')
    source_path = Path(filepath)
    print('ori',filepath)
    i += 1
    source_suffix = source_path.suffix
    print('str',pathstr)
    # 取目录的后两子为名称
    path_target = Path(pathname) / (pathstr[-2:]+str(i) + source_suffix)
    source_path.rename(path_target)
    print(path_target)
