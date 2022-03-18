# -*- coding:utf-8 -*-
from selenium import webdriver
import datetime
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
import pytesseract
from captcha2str import captcha2str

# from explicit_driver import *


driver = webdriver.Chrome(r"chromedriver")
# driver下载地址 https://chromedriver.storage.googleapis.com/index.html
# begin_time = "07:00:00" # 注意07的0
begin_time = "21:38:00" # 测试用时间


sso_username = ''
sso_passwd = ''
alipay_username = ''
alipay_passwd = ''

reserve_time = [7]  # 开始时间，此即为8~9, 9~10，24小时制！
# 现在学校的场馆预约好像有个bug，选8,10这种跳着的就只能选一个，2块场必须连续
priority = [12, 11, 10, 8, 5, 7, 6, 4, 3, 2, 9, 1]


def explicit_click(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    if EC.element_to_be_clickable(locator):
        driver.find_element(method, value).click()
    else:
        driver.execute_script("arguments[0].click();", driver.find_element(method, value))


def explicit_find(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    return driver.find_element(method, value)


def explicit_interact(method, value, driver=driver):
    locator = (method, value)
    WebDriverWait(driver, 20, 0.5).until(EC.element_to_be_clickable(locator))
    return driver.find_element(method, value)


def reserve(reserve_time, priority, driver=driver):
    for i in range((reserve_time[0] - 7) // 5):  # 跨页问题怎么搞
        explicit_click('xpath', "//*[@id='scrollTable']/div/table/thead/tr/td[6]/div/span/i")

    index = [(x - 7) % 5 + 2 for x in reserve_time]  # 转换时间对应下标
    for i in priority:
        blocks = []
        for j in index:
            blocks.append(explicit_find('xpath', '//*[@id="scrollTable"]/div/table/tbody/tr[%s]/td[%s]/div' % (i, j)))

        block1 = blocks[0]
        block2 = blocks[1] if len(blocks) == 2 else None
        if block1.get_attribute('class') == 'reserveBlock position free' and (
                not block2 or block2.get_attribute('class') == 'reserveBlock position free'):  # 场一空闲，场二不存在或也空闲
            block1.click()
            if block2:
                block2.click()

            # 同意协议并提交
            driver.find_element('class name', 'ivu-checkbox-input').click()
            reserve_button = driver.find_element('xpath',
                                                 '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[5]/div/div[2]')

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
            explicit_click('xpath',
                           '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/form/div/div[2]/div/div/label[1]/span[1]/input')
            explicit_click('xpath', '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div[2]')
            break
        else:
            continue
    else:
        print("all reserved!")


def pay(driver=driver):
    explicit_click('xpath', '/html/body/div[1]/div/div/div[3]/div[2]/div/div[3]/div[7]/div[2]/button')
    explicit_click('css selector',
                   'body > div:nth-child(18) > div.ivu-modal-wrap > div > div > div.ivu-modal-body > div.payHint > a')

    driver.switch_to.window(driver.window_handles[1])

    explicit_click('css selector', '#basic > a')
    explicit_click('css selector', '#mat-tab-content-0-0 > div > div > span:nth-child(1) > svg')
    explicit_click('css selector', '#J_changePayStyle')
    explicit_click('css selector', '#J_viewSwitcher')
    explicit_interact('css selector', '#J_tLoginId').send_keys(alipay_username)
    explicit_interact('css selector', '#payPasswd_rsainput').send_keys(alipay_passwd)

    capt_code = captcha2str('class name', 'checkCodeImg', driver)

    explicit_find('class name', 'ui-input-checkcode').send_keys(capt_code)
    explicit_click('css selector', '#J_newBtn')

    driver.switch_to.window(driver.window_handles[1])
    explicit_find('class name', 'sixDigitPassword').send_keys(alipay_passwd)
    explicit_click('css selector', '#J_authSubmit')



    return None


if __name__ == '__main__':

    now = datetime.datetime.now()
    begin_time_today = str(now.date()) + ' ' + begin_time
    begin_time_dt = datetime.datetime.strptime(begin_time_today, "%Y-%m-%d %H:%M:%S")
    one_minute_before = begin_time_dt - datetime.timedelta(minutes=1)

    while (now < one_minute_before):
        now = datetime.datetime.now()
        print("等待到达目标时间前一分钟:", now.time())

    print(now.time())
    print("到达目标时间前一分钟，开始启动浏览器内核")

    driver.get("https://cgyy.buaa.edu.cn/venue/Login")
    driver.maximize_window()

    # 点击进入场馆预约的统一认证界面，输入用户名密码、确认
    explicit_click('css selector', 'body > div.fullHeight > div > div > div > div > div.loginFlagWrap > a')
    driver.switch_to.frame("loginIframe")
    explicit_find('id', 'unPassword').send_keys(sso_username)
    explicit_find('id', 'pwPassword').send_keys(sso_passwd)
    explicit_click('class name', 'submit-btn')

    # 点击场地预约、选择学院路主馆羽毛球
    explicit_click('css selector', "div.funModule > div:nth-child(1)")
    explicit_click('css selector',
                   'body > div.fullHeight > div > div > div.discount > div.discountWrap > div > div.venueList > div:nth-child(2) > div.venueDetail > div.venueDetailBottom > div:nth-child(1)')

    WebDriverWait(driver, 20, 0.5).until(
        EC.url_changes('https://cgyy.buaa.edu.cn/venue/venue-introduce'))  # 检查click执行完毕，此后进入轮询等待状态

    now = datetime.datetime.now()
    while (now < begin_time_dt):
        now = datetime.datetime.now()
        print("等待到达目标时间:", now.time())


    driver.refresh()
    print(now.time(), "到达目标时间，正在刷新浏览器！")

    # 点两下日期向右（两天后），再点两下时间向后
    explicit_click('css selector', 'body > div.fullHeight > div > div > div.coach > div.venueSiteWrap > div > div.reservationStep1 > form > div > div > button:nth-child(3)')
    explicit_click('css selector', 'body > div.fullHeight > div > div > div.coach > div.venueSiteWrap > div > div.reservationStep1 > form > div > div > button:nth-child(3)')

    # 开始预约
    reserve(reserve_time, priority)

    # 支付
    pay()