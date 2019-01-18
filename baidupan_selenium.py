# coding=utf-8
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 存放文件和密码的文件mdata.txt 内容形式如下例子
# http://pan.baidu.com/s/1111111   PASS:pppp   http://pan.baidu.com/s/1111111   PASS:pppp

urlp = re.compile('https*://pan.baidu.com/s\S+')
# 生成urlpass字典
with open('mdata.txt') as f:
    text = f.read()
    urlpass = {url.group():re.search(url.group()+'\s+'+'PASS:\S+',text).group(0)[len(url.group()):].strip()[len('PASS:'):] for url in re.finditer(urlp,text)}
    urls = list(urlpass.keys())

for url in urls:
    print urls.index(url),' ',url,' ',urlpass[url]

# 控制开始和结束序号
x=0
y=-1
driver = webdriver.Chrome()

for url in urls[x:y]:
    print urls.index(url)
    print url,urlpass[url]
    driver.get(url)
    try:
        codeelem = WebDriverWait(driver,3).\
            until(EC.presence_of_element_located((By.CSS_SELECTOR,'form input[tabindex="1"]')))
        print driver.title
        codeelem.send_keys(urlpass.get(url))
        codeelem.send_keys(Keys.RETURN)
    except TimeoutException as e:
        print '没来及创建'

    try:
        # 等待超慢的网络加载
        WebDriverWait(driver,50).until(EC.title_contains('-'))
        if('mp' in driver.title):
            print driver.title
            continue
        # 属性自动调用get
        driver.current_window_handle
        print driver.title
    except TimeoutException as e:
        print '没来及打开新页面'

    try:
        selbutton = WebDriverWait(driver,5).\
            until(EC.presence_of_element_located((By.CSS_SELECTOR,'#shareqr li[data-key="server_filename"]>div>span')))
        selbutton.click()
    except TimeoutException as e:
        print e
    print '点击了全选'

    try:
        # 不管是否有全选，都要进入下载点击
        downloadbutton = WebDriverWait(driver,5).\
            until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.bar>div>a+a.g-button')))
        downloadbutton.click()
    except TimeoutException as e:
        print e
    print '点击了下载'

    passport_located = (By.CSS_SELECTOR, '#passport-login-pop')
    try:
        # 小于50M需要登录，扫码，或者直接关闭，后面手动下
        passport = WebDriverWait(driver,5).\
            until(EC.visibility_of_element_located(passport_located))
        print "扫码登录出现了"
        # 关闭
        driver.find_element(By.CSS_SELECTOR,'#passport-login-pop a.close-btn').click()
    except TimeoutException as e:
        print e
        print '扫码登录没等到'

    time.sleep(1)
    try:
        # 扫码登录已经消失
        passport = WebDriverWait(driver, 50). \
            until(EC.invisibility_of_element_located(passport_located))
        print '扫码登录关闭了，或没出现'
    except TimeoutException as e:
        print e
        print '扫码关闭没等到'

    # Backus-Naur 范式，引号取内容，|任一边
    # 路径表达式被用来在树中定位节点，路径表达式由序列的使用/或者//分割的一个或者多个步骤组成，
    # 开始于/或者//，开始位置的/的前面隐含了root的缩写，开始位置的//前面隐含了root/后辈的缩写。
    # /是路径操作符，为树中的本地节点构造表达式。左侧表达式必须返回一个节点序列。
    # 这个操作符要么返回一个节点序列，要么是非节点序列。
    # 缩写语法 缩写前向步@?节点测试 缩写反向步 ..

    human_dialog_located=(By.XPATH,'//div[@class="download-verify"]/../../..')
    try:
        humandialog = WebDriverWait(driver, 5).\
            until(EC.visibility_of_element_located(human_dialog_located))
        print '人识别出现了，手动处理'
    except TimeoutException as e:
        print '没有等到出现人验证'

    try:
        WebDriverWait(driver, 50). \
            until(EC.invisibility_of_element_located(human_dialog_located))
        print '人识别消失了'
    except TimeoutException as e:
        print '没有来及的处理人识别'

    # 首次启动网盘程序下载的提示，勾选弹出框上的选项，后面就不会再弹框了。

    # 小于50M的文件会提示，登录下载，这个我直接关掉了，以后可以手动下载。

    time.sleep(5)
driver.quit()




