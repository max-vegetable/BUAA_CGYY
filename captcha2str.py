# -*- coding:utf-8 -*-

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from skimage.metrics import structural_similarity
from PIL import Image
import numpy as np
import os


def captcha2str(method, value, driver):

    #有时，验证码是在输完密码之后才生成的，所以必须locate到验证码后再截图识别
    locator = (method, value)
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
    capt_img = driver.find_element(method, value)
    capt_img.screenshot('img/captcha.png') # 可以直接通过调用内部screenshot的方法静态存储

    images = []
    collections = os.listdir('captcha_collections')

    for i in range(10):
        img = Image.open('captcha_collections/%s' % collections[i]).convert('L')
        images.append(np.array(img))

    capt_img = Image.open('img/captcha.png').convert('L')
    capt_array = np.array(capt_img)

    maxSSIM, index = 0., 0
    for i in range(10):
        score = structural_similarity(images[i], capt_array)
        if score > maxSSIM:
            maxSSIM = score
            index = i

    return collections[index].replace('.png', '')