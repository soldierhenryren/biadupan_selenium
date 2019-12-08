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

# 准备一个正则对象re，用于后面的匹配字符串中的模式，反斜线加大S表示非空格字符，+表示1到任意个，顺便说一下.表示0到任意个。
urlp = re.compile('https*://pan.baidu.com/s\S+')
# 生成urlpass字典
# 使用with安全方便的创建文件对象，就在项目中所以没有绝对地址。
with open('mdata.txt') as f:
    # 直接从文件对象中读出内容，创建一个字符串对象text
    text = f.read()
    # 最外侧是字典生成式，最终要生成的是字典，左侧生成表达式是从冒号：左边，到冒号右顺序，url.group()先执行，取值循环表达式依次取出url值。
    # 使用正则对象的finditer方法可以得到网址匹配结果对象（注意不是网址字符串对象）的生成器，每一次顺次取一个匹配结果对象,匹配对象结果使用
    # group方法就可以得到匹配的网址字符串对象了，group就像一个列表一样，列表项就是网址，这是生成字典的key。
    # 正则对象的search方法，匹配模板是获取这个http://pan.baidu.com/s/1111111   PASS:pppp，反斜线加小s表示空字符。使用slice，就是[]
    # 获取   PASS:pppp，使用strip去掉空格，PASS:pppp，再用slice,就是[]获取到pppp。
    urlpass = {url.group():re.search(url.group()+'\s+'+'PASS:\S+',text).group(0)[len(url.group()):].strip()[len('PASS:'):] for url in re.finditer(urlp,text)}
    # 由于字典是无序的，所以后面不可能一次运行成功的情况下，必须保证按照固定的顺序来操作，就取前面的key的列表，就是网址的列表。列表是有序的。
    urls = list(urlpass.keys())

for url in urls:
    # 输出时候给每一个项编一个号。
    print(urls.index(url),' ',url,' ',urlpass[url])

# 这个是操作的主体，网络驱动器对象，承载所有操作。
driver = webdriver.Chrome()

# 控制开始和结束序号，0是第一个，-1是最后一个。运行中总是出现错误，可以从出错的地方再来过。
x=0
y=-1
for url in urls[x:y]:
    print urls.index(url)
    print url,urlpass[url]
    # 访问网盘地址
    driver.get(url)
    try:
        # 周期的自动查询访问url返回的网页，如果有指定的元素出现，就继续执行，否则就等着，但是最长不等过3秒，视网络情况而定。关于时间的设置
        # 一般来说都是宁长勿短，反正只要事实返回了，不管时间到了没有，都会继续执行的。

        # EC的定位对象的方法presence_of_element_located里面输入的论数（argument，我用以区别参数parameter），是一个tuple，包含一个
        # By对象的特征，标识这个元素的定位方法，我习惯于用CSS_SELECTOR,CSS元素选择器，前端的人都熟悉这个的。但是需要从子节点取父节点的
        # 时候，要用XPATH，是XML规范里定义的，相对于HTML的更加精准和严谨，但是十几年了也没见太发展，看来一般人的本性不喜欢严谨的。

        # CSS元素判定有4种条件：1、元素种类，比如这里的form表单，div，a等等，2、id，元素的身份证号，前面加一个#表示，3、元素的类，前面
        # 加一个.表示，4、特征方括号里面特征名=特征值，记得加引号。
        # CSS元素关系常用有3种，亲儿子们 > ,后代们 (空格) ,弟弟 + 规定了大概几十种吧，需要了就查一下。
        # 此处就表示百度网盘打开后需要你填写提取码的元素。
        codeelem = WebDriverWait(driver,3).\
            until(EC.presence_of_element_located((By.CSS_SELECTOR,'form input[tabindex="1"]')))
        # 输出浏览器对象的标题
        print driver.title

        # 填进去网址对应的字典中的值，就是提取码
        codeelem.send_keys(urlpass.get(url))
        # 在元素上模拟一个键盘回车的操作。
        codeelem.send_keys(Keys.RETURN)

    # 主要是捕捉超时异常，在3秒钟内没有返回包含提取码输入元素的页面
    except TimeoutException as e:
        print '没来及创建'

    try:
        # 等待超慢的网络加载，网盘下载的主页面看上去简单，其实一堆各种复杂的代理，访问，下载CSS样式，js脚本等等，所以50秒不为过。
        # 更郁闷的是，你能看到浏览器已经出现内容，甚至你都可以点击链接了，但是WebDriver认为还没有加载完，一般都要2、30秒。

        # 这一次使用的不是看元素是否出现，而是看浏览器对象标题是否包含-，这个百度网盘的特点。
        WebDriverWait(driver,50).until(EC.title_contains('-'))

        # 因为我需要过滤到一些特定名称的文件不下载，所以加这一个语句，因为百度网盘会把文件名称放到标题开头。
        if('sp' in driver.title):
            print driver.title
            # 跳出当前循环，进入下一个循环。找下一个网址去了。
            continue

        # 这个是个属性property，所以会自动调用get方法
        driver.current_window_handle
        print driver.title
    # 还是捕捉超时异常，50秒的等待啊，一般都在20秒就能返回。
    except TimeoutException as e:
        print '没来及打开新页面'

    # 页面终于返回成功了，下面要开始找全选框框了
    try:
        # shareqr是一个div的id号，这是最靠近目标元素，就是那个全选框了。找具有特征data-key值为server_filename的li元素，的亲儿子div
        # 的亲儿子span，就是那个全选框。
        selbutton = WebDriverWait(driver,5).\
            until(EC.presence_of_element_located((By.CSS_SELECTOR,'#shareqr li[data-key="server_filename"]>div>span')))
        # 在5秒钟之内找到元素，就模拟点击。
        selbutton.click()
    except TimeoutException as e:
        # 如果继上面页面加载完成后，5秒内找不到元素，就会引发异常，这里就捕捉到了，但是也有可能是因为就没有这个元素。
        print e
    # 到这里，说明一切OK，因为有的单独文件，页面上就没有这个元素的。也是正常的。
    print '点击了全选，或者单独的文件找不到全选框框'

    try:
        # 不管是否有全选，都要去找下载的按钮
        downloadbutton = WebDriverWait(driver,5).\
            until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.bar>div>a+a.g-button')))
        # 5秒内找到就点击
        downloadbutton.click()
    except TimeoutException as e:
        print e
    print '点击了下载，或者没有找到'

    # 点击下载之后有可能弹出一个让你扫码登录弹窗。
    passport_located = (By.CSS_SELECTOR, '#passport-login-pop')
    try:
        # 如果文件小于50M，则需要登录，扫码，我选择直接关闭，后面手动下
        passport = WebDriverWait(driver,5).\
            until(EC.visibility_of_element_located(passport_located))
        # 5秒钟之内出现了这个弹窗
        print "扫码登录出现了"
        # 关闭这个弹窗，主要是找到弹窗上的叉叉。
        driver.find_element(By.CSS_SELECTOR,'#passport-login-pop a.close-btn').click()
    # 如果5秒内没有出现弹窗，也是正常的。
    except TimeoutException as e:
        print e
        print '扫码登录没等到'

    # 点击关闭之后，小睡1秒，给系统一些反应时间
    time.sleep(1)

    # 等待这个弹窗消失的发生
    try:
        # 这个状态肯定发生的，因为要么是扫码登录关闭后消失了，也可能压根就没有出现过扫码弹窗，所以我多等一会50秒
        # 这个EC对象的方法是特定元素不可见。
        passport = WebDriverWait(driver, 50). \
            until(EC.invisibility_of_element_located(passport_located))
        print '扫码登录关闭了，或没出现'
    # 也有可能真没等到消失事件，也许是百度改了代码，上面的条件捕捉不到。
    except TimeoutException as e:
        print e
        print '扫码关闭没等到'

    # 因为要从子元素定位父元素，（这个弹窗消失和出现都是由上级元素决定的，所以要向外找）为何不使用其他定位方法，因为有些值，是随机出现，百度
    # 耍的小花样。动态生成元素，自动添加类名之类的，会变的。我这个办法比较稳当。

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

    # 手动输入验证码之后，回车，弹窗消失，这个事件会被等到，留出50秒来，足够你换三次验证码了。
    try:
        WebDriverWait(driver, 50). \
            until(EC.invisibility_of_element_located(human_dialog_located))
        print '人识别消失了'
    except TimeoutException as e:
        print '没有来及的处理人识别'

    # 最后注意的是

    # 首次会有启动网盘程序下载的提示，勾选弹出框上的选项，后面就不会再弹框了。

    # 小睡5秒，等待下一次循环，我没有关闭这个浏览器。而是直接访问下一个网址。
    time.sleep(5)

# 所有网址都访问完后，关闭浏览器，程序执行完毕。
driver.quit()

# 下面还有一个自动解压缩的，有时候下下来几百个压缩包，还都带密码，密码有时还不一样。


