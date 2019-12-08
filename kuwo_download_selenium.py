# coding=utf-8
import re
from urllib import urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
listurl = 'http://www.kuwo.cn/down/playlist/2388201203'
driver.get(listurl)
try:
    WebDriverWait(driver, 50).until(EC.title_contains('['))
    # 这个是个属性property，所以会自动调用get方法
    print driver.current_window_handle
except TimeoutException as e:
    print '没来及打开新页面'
try:
    mark_uls = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.name a')))
    i = 0
    for element in mark_uls:
        i+=1
        url = element.get_attribute('href')
        songid = url[len('http://www.kuwo.cn/down/single/'):-1]
        decode_url = 'http://player.kuwo.cn/webmusic/st/getNewMuiseByRid?rid=MUSIC_' + songid
        name = element.text
        print '\nXXXXXXXXXXXXXXXXXXXXXXXXX {:d} XXXXXXXXXXXXXXXXXXXXXXXXXX'.format(i)
        print name, decode_url
        response = urlopen(decode_url)
        rbody = response.read()
        print rbody
        pathre = re.compile('<mp3path>[^<]+')
        dlre = re.compile('<mp3dl>[^<]+')
        pathmach = re.search(pathre, rbody)
        if pathmach is None:
            continue
        path = pathmach.group(0)[len('<mp3path>'):]
        dlmach = re.search(dlre, rbody)
        if dlmach is None:
            continue
        dl = dlmach.group(0)[len('<mp3dl>'):]
        print path, dl
        target = ''.join(['http://', dl, '/resource/', path])
        print target
        rfile = urlopen(target)
        with open(name + '.mp3', 'wb') as af:
            af.write(rfile.read())
except TimeoutException as e:
    print '没来及打开新页面'
driver.quit()
