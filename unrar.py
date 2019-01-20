# coding=utf-8
import os.path
import pexpect
import py7zlib
import rarfile

# 压缩文件所在文件夹
root = 'file/path'
# 所有可能的密码。
pwl=['pppp','pppp']

# 目录下所有文件名称
flist = os.listdir(root)
# 过滤出正确的文件名称，比如名称前加点的。
rarlist = filter(lambda x:x.find('.') * (x.find('.7z') + x.find('.rar') + x.find('.zip'))>0 , flist)

for rar in rarlist:
    rarname = os.path.join(root, rar)
    print rarname
    if '.zip' in rarname[-5:]:
        # unzip zip
        print '使用.zip解压'
        try:
            for pw in pwl:
                # python标准库zipfile解压加密的超慢，所以使用pexpect直接调用系统中的unzip。先要确保unzip可以执行
                comand = ['unzip','-o','-d', root,'-P',bytes(pw),rarname]
                child = pexpect.spawn(' '.join(comand))
                index = child.expect(['incorrect password','replace',pexpect.EOF],timeout=None)
                if index ==0:
                    print '密码错误'
                    continue
                if index == 1:
                    print '重复文件自动替换-o选项无效'
                    child.sendline('yes')
                if index ==2:
                    print '密码正确，并解压'+pw
                    os.remove(rarname)
                    break
        except Exception as e:
            print e
            print 'zip解压异常'

    if '.7z' in rarname[-4:]:
        # unzip 7z
        print '使用.7z解压'
        try:
            for pw in pwl:
                # 7z库也是超慢，模仿unzip使用
                command = ['7za', 'x', rarname, '-o' + root, '-r', '-aoa', '-p' + pw]
                child = pexpect.spawn(' '.join(command))
                index = child.expect(['Wrong password', pexpect.EOF], timeout=None)
                if index == 0:
                    print '密码错误'
                    continue
                if index == 1:
                    print '密码正确，并解压' + pw
                    os.remove(rarname)
                    break
        except Exception as e:
            print e
            print '7z解压失败'

    if '.rar' in rarname[-5:]:
        # unrar rar
        print '使用rar解压'
        try:
            for pw in pwl:
                try:
                    rarfile.RarFile(rarname).extractall(path=root,pwd=pw)
                    os.remove(rarname)
                    print 'rar密码正确'+pw
                    break
                except rarfile.RarWrongPassword as er:
                    print 'rar 密码错误'
                    continue
        except Exception as e :
            print e
            print 'rar解压失败'



