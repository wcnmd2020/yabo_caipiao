import time
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import copy
import uuid
import hashlib
import random
import json
import os


try:

    reurl = requests.get('http://api.fuliduoduo.xyz:48081/string/userid=xxm')

    reurl_dict = json.loads(reurl.json())

except:

    print('network error !')

    exit()


#全局参数
print('')
print(reurl_dict['version_str'])
print(reurl_dict['huanying_str'])
print('')

# 盈利总和字典
profittotal = {}

# 每组0-9数字在网页代码里对应的编号
all_number = {0: 7, 1: 8, 2: 9, 3: 10, 4: 11, 5: 12, 6: 13, 7: 14, 8: 15, 9: 16}

# 每期5个数字在网页代码里对应的拼音
pinyin_number = {1: 'diyiqiu', 2: 'dierqiu', 3: 'disanqiu', 4: 'disiqiu', 5: 'diwuqiu'}

# 会话保持
session_requests = requests.session()

browser = None

loadingTotal = 0

repeatTotal = 0

xiazhu_monery_list = []


# 下注操作
def xiao_zhu(account):

    xiazhu_monery_list = ['1','1','1','1','1','1','1','1','1','2','2','2','2','2','3','3','3','4','4','5','5',
                                 '6','6','7','8','9','10','11','12','13','15','17','19','21','23','26','29','32','35',
                                 '39','44','49','55','61','68','75','84','93','104','120','0']

    # 当天玩的局数情况，初始值为0.
    junshu = 0

    while True:

        # 随机取球位
        qiuwei = random.randint(1, 5)

        # 生成要下注的数字
        xiazhu_number_list = get_num()

        time.sleep(3)

        # 第次赢中后，暂停70秒，再接着开始
        if junshu != 0:

            print('sleep 70 start')

            time.sleep(70)

        # 程序运行时段限制
        shizhong = time.strftime("%H")

        # 每天晚上23点关闭
        if shizhong == '23':

            print('game server stop', '设定时间已到，程序自动停止')

            browser.close()

        # 初始局为1
        junshu += 1

        # 中奖暗号，默认为0，中奖后为4
        aoc = 0

        # 初始本钱为0
        benqian_monery = 0

        # 期号对应的下注数字
        qihao_shuzi = {}

        # 初始化时间戳
        now_time = time.time()

        # 已下注的期号
        yixiazhu = []

        # 打印局数信息
        print('@@@@@@@@@@@@@@@@第', junshu, '大局@@@@@@@@@@@@@@@@@@@@@')

        # 发送电子邮件告知局数
        print("第%i大局开始" % junshu, '当前账户余额%s元' % get_monery())

        # 期号初始值：空
        qiao_prior = 'kong'

        # 开始循环下注,计划多少小局为一个循环。然后+1，比如计划30局，就要写成31.
        all_pan = 41  # 这里为40小局为一个大局（循环）

        for pan in range(all_pan):

            # 当前下注的金额
            xiazhu_monery = int(xiazhu_monery_list[pan])

            # 当前下注的号码
            xiazhu_number = int(xiazhu_number_list[pan])

            # 当前如果中奖，将赢得的金额。
            if pan > 0:
                prior_xiazhu_monery = int(xiazhu_monery_list[pan-1])
                zhongjiang_monery = prior_xiazhu_monery * 9.85
            else:
                zhongjiang_monery = 1

            # 毛利
            maoli_monery = zhongjiang_monery - benqian_monery

            # 本金每局会增加
            benqian_monery = benqian_monery + xiazhu_monery

            # 程序是否已跑完
            if pan == all_pan - 1:
                status = 'stop'
            else:
                status = 'run'

            print('--------------第%i大局：%i小局--------------：' % (junshu, pan+1))

            zhijie = 0

            # 当前时间
            localtime = time.asctime(time.localtime(time.time()))

            # 打印当前时间
            print("本地时间为 :", localtime)

            # 判断状态是否为已中奖，中奖为stop。一般为最后一小局。
            if status == 'stop':

                while True:
                    # 获取当前的开奖号码
                    kaijiang_list = get_number()

                    # 获取当前的期号
                    input_qihao = browser.find_element_by_css_selector("body > div.app > div.lottery.openRightMenu > "
                                                                       "div.sidebar-menu.rightMenu > div.menu-content > "
                                                                       "div.standard-menu > div.recent-lottery > "
                                                                       "div.lottery-recently.double.SSC > "
                                                                       "ul.zhenghe.recently-list.list.recently-list-body > "
                                                                       "li:nth-child(1) > div.main-issue")

                    qihao_local = input_qihao.text

                    # 获取的当前期号如果没变，就等待5秒钟
                    if qiao_prior == qihao_local:

                        # print('当前开奖期号：', qihao_local)
                        time.sleep(5)
                        continue

                    else:

                        print('当前开奖期号：', qihao_local)

                    # 第一次运行时，期号值为字符‘kong’，然后保存下来当前的期号。
                    if qiao_prior == 'kong':

                        qiao_prior = qihao_local

                    # 当前开奖的号码是否和上一期保存的号码是否一致，一致就通知。
                    elif int(kaijiang_list[qiuwei - 1]) == prior_number:

                        print('中奖了6666666>>>:', prior_number)

                        print('第%i大局:%i小局中奖了，毛利:%.2f元' % (junshu, pan, maoli_monery),
                               '当前总盈利%.2f元' % profit_total(maoli_monery, junshu))

                        break

                    print('当前期号：', qihao_local, '开奖号码：', kaijiang_list, '我的下注号码：', prior_number,
                          '对应的开奖号码：', qihao_kaijiang)

                    print('40局没中奖，程序停止', '当前账户余额%s元' % get_monery())

                    # 关闭浏览器
                    browser.close()

                    # 退出
                    exit()
                    break

            # 这里因为没有唯一ID可供抓取，只能用绝对路径了
            # 下注数字对应的金额框路径
            input_number = browser.find_element_by_css_selector("body > div.app > div.lottery.openRightMenu > "
                                                                "div.lottery-wrapper > div > div.lottery-content > "
                                                                "div.lottery-content-scroll > div.bet-wrapper > div "
                                                                "> div.double-balls-plate.zhenghe > "
                                                                "div.double-series.%s > div.playGroup-list > "
                                                                "div:nth-child(%i) > div.amount > input"
                                                                % (pinyin_number[qiuwei], all_number[xiazhu_number]))

            while True:
                # 当前时间戳
                now_time2 = time.time()

                # 获取当前的开奖号码
                kaijiang_list = get_number()

                # 获取当前的期号
                input_qihao = browser.find_element_by_css_selector("body > div.app > div.lottery.openRightMenu > "
                                                                   "div.sidebar-menu.rightMenu > div.menu-content > "
                                                                   "div.standard-menu > div.recent-lottery > "
                                                                   "div.lottery-recently.double.SSC > "
                                                                   "ul.zhenghe.recently-list.list.recently-list-body > "
                                                                   "li:nth-child(1) > div.main-issue")

                qihao_local = copy.deepcopy(input_qihao.text)

                if pan == 0:

                    tmp_qihao = int(qihao_local)

                    liangju = 1

                    # 启示期号初始值
                    qihao_shuzi[qihao_local] = '13'

                    localtime = time.strftime("%d", time.localtime())

                    a = list(localtime)

                    for z in range(40):

                        tmp_qihao += 1

                        if a[0] == '0':

                            tmp = '0' + str(tmp_qihao)

                        else:

                            tmp = str(tmp_qihao)

                        qihao_shuzi[tmp] = xiazhu_number_list[z]

                    print('当前开奖期号：', qihao_local)

                elif now_time2 > now_time and qiao_prior != qihao_local and get_kaijiang_time() == '1':

                    print('当前开奖期号>>>>：', qihao_local)

                elif now_time2 > now_time and get_kaijiang_time() == '1':

                    # 等于1就代理是直接下注的，0非
                    zhijie = 1

                    print('已经超过60秒还没开奖，直接下注，当前获取的开奖期号：%s' % qihao_local)

                    # 这里处理开奖超时的情况
                    ab = int(qihao_local) + 1

                    abab = '0' + str(ab)

                    yixiazhu.append(abab)

                # 获取的当前期号如果没变，就等待5秒钟
                elif qiao_prior == qihao_local:

                    # print('当前开奖期号：', qihao_local)
                    time.sleep(5)

                    continue

                else:

                    print('当前开奖期号：', qihao_local)

                aaacc = qihao_shuzi[qihao_local]

                # 第一次运行时，期号值为字符‘kong’，然后保存下来当前的期号。
                if qiao_prior == 'kong':

                    qiao_prior = qihao_local

                # 当前开奖的号码是否和上一期保存的号码是否一致，一致就通知。
                elif kaijiang_list[qiuwei-1] == aaacc:

                    print('中奖了6666666>>>:', qihao_shuzi[qihao_local])

                    print('第%i大局:%i小局中奖了，毛利:%.2f元' % (junshu, pan, maoli_monery),
                           '当前总盈利%.2f元' % profit_total(maoli_monery, junshu))

                    # 中奖后的独有暗号
                    aoc = 4

                    break

                # 将当前的期号和对应的开奖号码记录下来
                # qihao_kaijiang 是str类型
                qihao_kaijiang = kaijiang_list[qiuwei-1]

                if pan == 0:
                    print('当前期号：', qihao_local, '开奖号码：', kaijiang_list, '我的下注号码：', '无', '我选的开奖号码：', '无')

                else:

                    # 这期我选的对应位置开奖号码
                    wxdkjhm = qihao_kaijiang

                    print('当前期号：', qihao_local, '开奖号码：', kaijiang_list, '我的下注号码：', prior_number, '对应的开奖号码：', wxdkjhm)

                if zhijie == 0:
                    # 保存当期的下注号码，以备下一期调用
                    prior_number = xiazhu_number

                    # 记录当前期号，以备下一期调用
                    qiao_prior = qihao_local

                    if liangju == 100:

                        print('小局内循环')

                        time.sleep(3)

                        liangju = 1
                        continue

                break

            # 中奖了就跳出循环，重新开始下一轮
            if aoc == 4:
                break

            # 往指定的输入框里写数字金额，字符类型为：int
            if zhijie == 1:
                input_number.send_keys(xiazhu_monery)

                # 单小局开两个号处理方法
                liangju = 100

            elif qihao_local in yixiazhu:

                print('此轮不用下注，已下0')


            else:

                input_number.send_keys(xiazhu_monery)

            print('下一期期号:%i,下注：%i元' % (int(qihao_local) + 1, xiazhu_monery))

            time.sleep(2)

            while True:

                print('------开始按“立即投注”按钮------')

                if zhijie == 1:

                    print('继续')

                elif qihao_local in yixiazhu:

                    print('此轮不用下注，已下1')

                    break

                # “立即投注”按钮
                try:

                    queding = browser.find_element_by_css_selector("body > div.app > div.lottery > div.lottery-wrapper"
                                                                   " > div > div.lottery-content > div.statistic-wrap"
                                                                   " > div > div > div:nth-child(3) > div")

                    time.sleep(2)

                    ActionChains(browser).move_to_element(queding).click().perform()

                except:

                    print('“立即投注”按钮报错，等待3秒重启按“立即投注”。')

                    print('投注按钮报错', '当前账户余额%s元' % get_monery())

                    time.sleep(3)

                    continue

                break

            if zhijie == 1:
                print('继续2')

            elif qihao_local in yixiazhu:
                print('此轮不用下注，已下2')
                # 当前时间戳
                now_time = time.time() + 50
                continue

            time.sleep(2)

            # 开始确认按钮
            try:
                zqd = browser.find_element_by_css_selector("#modals-container > div > div > div.v--modal-box.v--modal"
                                                           " > div > div.modal-btns > button.confirm")

                ActionChains(browser).move_to_element(zqd).click().perform()


            except:

                print('确定按钮报错', '当前账户余额%s元' % get_monery())

            # 已经下注的期数，写入列表里面
            yixiazhu.append(qihao_local)

            # 当前时间戳
            now_time = time.time() + 45

            time.sleep(2)

            try:

                # 关闭余额不足提示
                browser.find_element_by_css_selector("body > div.app > div.v--modal-overlay > div > "
                                                     "div.v--modal-box.tip-modal.v--modal-box-autowidth > div > "
                                                     "div.modal-btns > button").click()

                print('您的余额不足，请前往充值')
                time.sleep(2)

            except:

                print('余额充足')

            # 清空投注输入数字
            qingkong = browser.find_element_by_css_selector("body > div.app > div.lottery.openRightMenu > "
                                                            "div.lottery-wrapper > div > div.lottery-content > "
                                                            "div.statistic-wrap > div > div > div.reset > div")

            time.sleep(1)

            ActionChains(browser).move_to_element(qingkong).click().perform()

            time.sleep(1)

            ActionChains(browser).move_to_element(qingkong).click().perform()

            print("已重置下注记录")


# 获取开奖计时
def get_kaijiang_time():
    # 秒针十位
    input_time = browser.find_element_by_css_selector("body > div.app > div.lottery.openRightMenu > div.lottery-wrapper"
                                                      " > div > div.lottery-content > div.lottery-info-wrap >"
                                                      " div.lottery-info.lottery-info-show.SSC > div:nth-child(2) > div"
                                                      " > div > div.currentIssue-right > div > div.lottery-counter >"
                                                      " div:nth-child(5) > div.num_left")
    # 秒针个位
    input_time_ge = browser.find_element_by_css_selector("body > div.app > div.lottery.openRightMenu > div.lottery-wrapper"
                                                      " > div > div.lottery-content > div.lottery-info-wrap >"
                                                      " div.lottery-info.lottery-info-show.SSC > div:nth-child(2) > div"
                                                      " > div > div.currentIssue-right > div > div.lottery-counter >"
                                                      " div:nth-child(5) > div.num_right")

    print('距离开奖倒计时>00:', input_time.text + input_time_ge.text)

    return input_time.text


# 获取当期号码
def get_number():

    try:
        get_req = get_kaijiang_time()

        while '4' != get_req and '3' != get_req and '2' != get_req and '1' != get_req and '5' != get_req:

            time.sleep(5)

            get_req = get_kaijiang_time()

    except:

        print('获取当前号码失败', '当前账户余额%s元' % get_monery())

        time.sleep(1)

        # 再试一次
        get_req = get_kaijiang_time()

        while '4' != get_req and '3' != get_req and '2' != get_req and '1' != get_req and '5' != get_req:
            time.sleep(5)

            get_req = get_kaijiang_time()

        print('获取当前号码恢复正常', '当前账户余额%s元' % get_monery())

    # 开奖数
    list_number = []

    # 每期一共5个数字
    number = [1, 2, 3, 4, 5]

    for n in number:

        input_number = browser.find_element_by_css_selector("body > div.app > div.lottery.openRightMenu > "
                                                            "div.sidebar-menu.rightMenu > div.menu-content > "
                                                            "div.standard-menu > div.recent-lottery > "
                                                            "div.lottery-recently.double.SSC > "
                                                            "ul.zhenghe.recently-list.list.recently-list-body > "
                                                            "li:nth-child(1) > div.main-code > span:nth-child(%i) >"
                                                            " i > span" % n)

        if input_number.text != '\n':

            list_number.append(input_number.text)

    lst = copy.deepcopy(list_number)

    # 返回开奖号码队列
    return lst


# 模仿浏览器登录行为
def BrowserLogin(account, password):

    global loadingTotal

    time.sleep(1)

    loadingTotal = loadingTotal + 1

    # 输入用户名
    user_login = browser.find_element_by_css_selector('#app > div > div.A0n_A07 > div > div > div.A0n_A0v > div.A0n_Az9 > div:nth-child(1) > div > input[type=text]')

    user_login.send_keys(account)

    # 输入密码
    passwd_login = browser.find_element_by_css_selector('#app > div > div.A0n_A07 > div > div > div.A0n_A0v > div.A0n_Az9 > div:nth-child(2) > div > input[type=password]')

    passwd_login.send_keys(password)

    # 等待1秒
    time.sleep(1)

    # 无需验证码，登陆
    browser.find_element_by_css_selector('#app > div > div.A0n_A07 > div > div > div.A0n_A0v > div.A0n_Az9 > div.A0n_A0c > button').click()

    loadingTotal = 0

    time.sleep(4)

    # 关闭‘重要公告’
    try:
        browser.find_element_by_css_selector('#app > div > div:nth-child(2) > div:nth-child(2) > '
                                             'div.fY_kE > div > div.fY_kI > span').click()

    except:

        print('请手动关闭公告浮窗。')

    time.sleep(5)

    # 关闭‘重要公告’
    try:
        browser.find_element_by_css_selector('#noticeAlert > div > div > div > div.AxM_Rx > div.AxM_AaI > div.AxM_AaK > button.AxM_Bn').click()

    except:
        print('请手动关闭公告浮窗')

    time.sleep(5)

    # 进入到幸运分分彩
    # 点网页上层的‘彩票’按钮

    browser.find_element_by_css_selector('#app > div > div:nth-child(2) > div.AJv_AJx > div.AJv_AJ5 > div > div.AJv_AJ9 > div.AJv_AKE > ul > li:nth-child(6) > div').click()

    time.sleep(10)

    # 点击‘进入游戏’
    browser.find_element_by_css_selector('#app > div > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > ul > li > div.AYY_Jj > div.AYY_eY.AYY_Jr > div.AYY_ec').click()

    time.sleep(3)

    # 关闭“单期盈利上限”公告栏
    try:
        browser.find_element_by_css_selector('#modals-container > div > div > div.v--modal-box.v--modal.v--modal-box-autowidth > div > div.content-wrap > div.content-footer > div.btn').click()

        time.sleep(1)

    except:

        print('没有展示公告栏：一')

    time.sleep(10)

    # 开始进入‘腾讯分分彩’

    # 此网页使用了内嵌技术，找到iframe元素
    iframe = browser.find_element_by_tag_name('iframe')

    # 进入内嵌地址
    browser.switch_to.frame(iframe)

    # 进入内嵌地址后，点击幸运分分彩图标，进行其下注界面
    browser.find_element_by_css_selector("body > div.app > div.trendWrapper > div > div.content > div.homePage > "
                                         "div.page__left > div.swiper-container.flip-nav.swiper-container-initialized.swiper-container-horizontal > "
                                         "div.swiper-wrapper > div.swiper-slide.swiper-1.swiper-slide-next > div > "
                                         "div > div.flip-box__back").click()

    # 关闭“单期盈利上限”公告栏
    try:
        browser.find_element_by_css_selector("#modals-container > div > div > "
                                             "div.v--modal-box.v--modal.v--modal-box-autowidth > div > div.content-wrap"
                                             " > div.content-footer > div.btn").click()

        time.sleep(1)

    except:

        print('没有展示公告栏：二')

    time.sleep(1)

    # 开始下注操作
    xiao_zhu(account)

    time.sleep(10)

    # 释放iframe，返回主页面
    browser.swtch_to.default_content()

    browser.close()


# 当天盈利总和
def profit_total(maoli, dajun):  # 毛利，第几大局

    profittotal[dajun] = maoli

    tmp = 0

    for p in profittotal.values():

        tmp += p

    return tmp


# 获取当前账号余额
def get_monery():

    yu_e = browser.find_element_by_css_selector("body > div.app > div.lottery.openRightMenu > div.lottery-wrapper > "
                                                "div > div.lottery-content > div.statistic-wrap > div > div > "
                                                "div.balance-box > div > span > span.balance-num-area")

    return yu_e.text


def get_mac_addr():

    m = hashlib.sha224()

    mac_add = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()

    mac_add_byte = bytes(mac_add, encoding='utf-8')

    m.update(mac_add_byte)

    return m.hexdigest()


def get_num():

    xiazhu_number_list = []

    for i in range(51):

        xiazhu_number_list.append(str(random.randint(0, 9)))

    return xiazhu_number_list


def login_user():

    print('请输入您的亚博账号和密码'.center(50, '*'))
    admin_id = input("请输入您的账号 >>>:").strip()
    admin_pwd = input("请输入您的密码 >>>:").strip()

    if admin_id and admin_pwd:

        return (admin_id, admin_pwd)

    else:

        print('请输入亚博平台的账号和密码')

        return 'nook'


# 从用户信息文件里提取数据
def read_user_info(user_db_file):

    if os.path.exists(user_db_file):
        with open(user_db_file, 'r', encoding='utf-8') as r:
            user_data = json.load(r)
        return user_data
    else:
        return 0


# 把用户数据写入信息文件
def write_user_info(user_db_file, data):

    with open(user_db_file, 'w', encoding='utf-8') as w:
        json.dump(data, w)
        return 1
    return 0


if __name__ == '__main__':
    # 程序运行路径
    path = os.path.dirname(os.path.abspath(__file__))

    # 储存亚博账号信息路径
    yb_path_file = path + '/' + 'yabo.json'
    yb_userinfo = read_user_info(yb_path_file)

    # 储存下注倍率信息路径
    bl_path_file = path + '/' + 'beilu.json'
    bl_userinfo = read_user_info(bl_path_file)

    if bl_userinfo:

        beishu = bl_userinfo['beilu']

        print("您当前的倍率是：%s" % beishu)

    else:
        while True:
            beishu = input("请输入你要想玩的倍数，1为默认，2为两倍，3为三倍，以此类推>>>: ").strip()

            if beishu.isdigit():

                data = {"beilu": beishu}
                write_user_info(bl_path_file, data)

                break

            else:

                print('请输入正确的数字')


    # 登陆亚博账号
    if yb_userinfo:

        ybuu = yb_userinfo['user']
        ybpp = yb_userinfo['passwd']

        print("您的亚博账号为：%s，密码为：%s" % (ybuu, ybpp))

    else:
        while True:

            rea = login_user()

            if rea != 'nook':

                ybuu = rea[0]
                ybpp = rea[1]

                data = {"user": ybuu, "passwd": ybpp}
                write_user_info(yb_path_file, data)

                break

    # 获取谷歌浏览器插件
    browser = webdriver.Chrome()

    # 打开亚博网站
    browser.get("https://www.yabovip66.com/login")

    # 网站的账号和密码
    BrowserLogin(ybuu, ybpp)

