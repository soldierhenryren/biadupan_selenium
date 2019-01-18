# coding=utf-8
import os.path
import py7zlib
import rarfile
# 压缩文件所在文件夹
root = '/Volumes/dirname/subdirname'
flist = os.listdir(root)
rarlist = filter(lambda x:x.find('.') * (x.find('.7z') + x.find('.rar')>0) , flist)
# 不支持utf-8，不能用中文
pwl=['password','password']
for rar in rarlist:
    rarname = os.path.join(root, rar)
    print rarname
    if '.7z' in rarname[-4:]:
        # unzip 7z
        print '使用.7z解压'
        try:
            for pw in pwl:
                with open(rarname, 'rb') as f:
                    try:
                        f7z = py7zlib.Archive7z(f,password=pw)
                        if len(f7z.getnames()):
                            for name in f7z.getnames():
                                of = os.path.join(root,name)
                                od = os.path.dirname(of)
                                if not os.path.exists(od):
                                    os.makedirs(od)
                                with open(of,'wb') as o:
                                    o.write(f7z.getmember(name).read())
                            os.remove(rarname)
                            print '7z密码正确'
                            break
                    except py7zlib.WrongPasswordError as er:
                        print '7z密码错误，换一个'
                        continue
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
                    print 'rar密码正确'
                    break
                except rarfile.RarWrongPassword as er:
                    print 'rar 密码错误'
                    continue
        except Exception as e :
            print e
            print 'rar解压失败'



