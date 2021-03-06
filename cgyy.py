# -*- coding:utf-8 -*-
from selenium import webdriver
import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from captcha2str import captcha2str
import yaml

driver = webdriver.Chrome(r"chromedriver")
# driver下载地址 https://chromedriver.storage.googleapis.com/index.html
driver.maximize_window()

begin_time = "07:00:00"  # 注意07的0

conf_file = open('configs/default.yaml', 'r')
configs = yaml.load(conf_file, Loader=yaml.Loader)

reserve_time = configs['reserve_time']  # 开始时间，此即为8~9, 9~10，24小时制！
# 现在学校的场馆预约好像有个bug，选8,10这种跳着的就只能选一个，2块场必须连续
priority = configs['priority']


def explicit_click(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 60,
                  0.5).until(EC.presence_of_element_located(locator))
    if EC.element_to_be_clickable(locator):
        driver.find_element(method, value).click()
    else:
        driver.execute_script("arguments[0].click();",
                              driver.find_element(method, value))


def explicit_find(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 30,
                  0.5).until(EC.presence_of_element_located(locator))
    return driver.find_element(method, value)


def explicit_find_short(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 5,
                  0.5).until(EC.presence_of_element_located(locator))
    return driver.find_element(method, value)


def explicit_interact(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    return driver.find_element(method, value)


def reserve(reserve_time, priority, driver=driver):
    # 点两下日期向右（两天后），再点两下时间向后
    explicit_click(
        'css selector',
        'body > div.fullHeight > div > div > div.coach > div.venueSiteWrap > div > div.reservationStep1 > form > div > div > button:nth-child(3)'
    )
    explicit_click(
        'css selector',
        'body > div.fullHeight > div > div > div.coach > div.venueSiteWrap > div > div.reservationStep1 > form > div > div > button:nth-child(3)'
    )

    for i in range((reserve_time[0] - 7) // 5):  # 跨页问题怎么搞
        explicit_click(
            'xpath',
            "//*[@id='scrollTable']/div/table/thead/tr/td[6]/div/span/i")

    index = [(x - 7) % 5 + 2 for x in reserve_time]  # 转换时间对应下标
    for i in priority:
        blocks = []
        for j in index:
            blocks.append(
                explicit_find(
                    'xpath',
                    '//*[@id="scrollTable"]/div/table/tbody/tr[%s]/td[%s]/div'
                    % (i, j)))

        block1 = blocks[0]
        block2 = blocks[1] if len(blocks) == 2 else None
        if block1.get_attribute('class') == 'reserveBlock position free' and (not block2 or block2.get_attribute('class') == 'reserveBlock position free'):  # 场一空闲，场二不存在或也空闲
            block1.click()
            if block2:
                block2.click()

            # 同意协议并提交
            driver.find_element('class name', 'ivu-checkbox-input').click()
            reserve_button = driver.find_element(
                'xpath',
                '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[5]/div/div[2]'
            )

            # 轮训检查提交按钮是否高亮
            # while True:
            #     if reserve_button.get_attribute('style') != 'background: rgb(238, 238, 238);':
            #         reserve_button.click()
            #         break
            reserve_button.click()

            # 选同伴和提交
            """
            选同伴处，label后面的index为同伴index，从1开始，如有需要可以改为1。
            span后面的1指checkbox，不要改
            """
            explicit_click(
                'xpath',
                '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/form/div/div[2]/div/div/label[%s]/span[1]/input'
                % configs['candidate'])
            explicit_click(
                'xpath',
                '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div[2]'
            )
            print(datetime.datetime.now().time(), "预约成功！进行可能的异常排查……")
            try:
                # 当出现预约错误时返回尝试重新预约
                err_element = explicit_find_short(
                    'css selector',
                    'body > div:nth-child(21) > div.ivu-modal-wrap > div > div > div > div > div.ivu-modal-confirm-body > div'
                )
                if "同伴存在时间冲突" in err_element.text:
                    print("候选人/同伴存在时间冲突，预约失败！")
                else:
                    print("场地下手慢了一点，正在重新选择……")
                    driver.refresh()
                    reserve(reserve_time, priority, driver=driver)
            except:
                print(datetime.datetime.now().time(), "预约无异常！进入付款页面……")
            return None
        else:
            continue
    else:
        print("all reserved!")


def pay(driver=driver):
    explicit_click(
        'xpath',
        '/html/body/div[1]/div/div/div[3]/div[2]/div/div[3]/div[7]/div[2]/button'
    )
    explicit_click(
        'css selector',
        'body > div:nth-child(18) > div.ivu-modal-wrap > div > div > div.ivu-modal-body > div.payHint > a'
    )

    driver.switch_to.window(driver.window_handles[1])

    explicit_click('css selector', '#basic > a')

    try:
        print(datetime.datetime.now().time(), '准备支付，首先检查北航支付系统是否出现故障……')
        while (explicit_find_short('xpath', '/ html / body / pre')):
            print(datetime.datetime.now().time(), '支付系统异常，尝试重新进入……')
            driver.back()
            explicit_click('css selector', '#basic > a')
    except:
        print(datetime.datetime.now().time(), '支付系统无异常，进行支付……')
        pass

    explicit_click(
        'css selector',
        '#mat-tab-content-0-0 > div > div > span:nth-child(1) > svg')
    explicit_click('css selector', '#J_changePayStyle')
    explicit_click('css selector', '#J_viewSwitcher')
    explicit_interact('css selector',
                      '#J_tLoginId').send_keys(configs['alipay']['user'])
    explicit_interact('css selector', '#payPasswd_rsainput').send_keys(
        configs['alipay']['passwd'])

    capt_code = captcha2str('class name', 'checkCodeImg', driver)

    explicit_find('class name', 'ui-input-checkcode').send_keys(capt_code)
    explicit_click('css selector', '#J_newBtn')

    driver.switch_to.window(driver.window_handles[1])
    explicit_find('class name',
                  'sixDigitPassword').send_keys(configs['alipay']['passwd'])
    explicit_click('css selector', '#J_authSubmit')

    print(datetime.datetime.now().time(), "支付成功！祝你打球愉快~")
    return None


if __name__ == '__main__':

    now = datetime.datetime.now()
    begin_time_today = str(now.date()) + ' ' + begin_time
    # begin_time_dt = datetime.datetime.strptime(begin_time_today, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=1) # 0点之前使用
    begin_time_dt = datetime.datetime.strptime(begin_time_today, "%Y-%m-%d %H:%M:%S")  # 0点之后/测试时使用
    one_minute_before = begin_time_dt - datetime.timedelta(minutes=1)

    while (now < one_minute_before):
        now = datetime.datetime.now()
        print("等待到达目标时间前一分钟:", now.time())

    print(now.time(), "到达目标时间前一分钟，开始启动浏览器内核")

    driver.get("https://cgyy.buaa.edu.cn/venue/Login")

    # 点击进入场馆预约的统一认证界面，输入用户名密码、确认
    explicit_click(
        'css selector',
        'body > div.fullHeight > div > div > div > div > div.loginFlagWrap > a'
    )
    driver.switch_to.frame("loginIframe")
    explicit_find('id', 'unPassword').send_keys(configs['sso']['user'])
    explicit_find('id', 'pwPassword').send_keys(configs['sso']['passwd'])
    explicit_click('class name', 'submit-btn')

    # 点击场地预约、选择学院路主馆羽毛球
    explicit_click('css selector', "div.funModule > div:nth-child(1)")

    now = datetime.datetime.now()
    while (now < begin_time_dt):
        now = datetime.datetime.now()
        print("等待到达目标时间:", now.time())

    print(now.time(), "到达目标时间，开始抢场地！")

    explicit_click(
        'css selector',
        'body > div.fullHeight > div > div > div.discount > div.discountWrap > div > div.venueList > div:nth-child(2) > div.venueDetail > div.venueDetailBottom > div:nth-child(1)'
    )

    # WebDriverWait(driver, 30, 0.5).until(
    #     EC.url_changes('https://cgyy.buaa.edu.cn/venue/venue-introduce'))  # 检查click执行完毕，此后进入轮询等待状态

    # driver.refresh()

    # 开始预约
    reserve(reserve_time, priority)

    # 支付
    pay()
