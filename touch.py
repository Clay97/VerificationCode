import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiying import Chaojiying_Client
from selenium.common.exceptions import TimeoutException

#12306登陆账号
EMAIL = 'UserName'
#12306登陆密码
PASSWORD = 'Passworrd'
#超级鹰账号、密码、软件ID、验证码类型ID
CHAOJIYING_USERNAME = 'UserName'
CHAOJIYING_PASSWORD = 'Passworrd'
CHAOJIYING_SOFT_ID =  123456
CHAOJIYING_KIND = 9004

class touch():
    def __init__(self):
        self.url = 'https://kyfw.12306.cn/otn/resources/login.html'
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, 10)
        self.email = EMAIL
        self.password = PASSWORD
        self.chaojiying = Chaojiying_Client(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)

    def __del__(self):
        self.browser.close()

    def open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.browser.get(self.url)
        #切换至账号登陆
        time.sleep(5)
        login = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,'login-hd-account')))
        login.click()
        email = self.wait.until(EC.presence_of_element_located((By.ID, 'J-userName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'J-password')))
        email.send_keys(self.email)
        password.send_keys(self.password)

    def get_touclick_element(self):
        """
        获取验证图片对象
        :return: 图片对象
        """
        element = self.wait.until(EC.presence_of_element_located((By.ID, 'J-loginImg')))
        return element

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        element = self.get_touclick_element()
        time.sleep(2)
        location = element.location
        size = element.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_touclick_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_points(self, captcha_result):
        """
        解析识别结果
        :param captcha_result: 识别结果
        :return: 转化后的结果
        """
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def touch_click_words(self, locations):
        """
        点击验证图片
        :param locations: 点击位置
        :return: None
        """
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_touclick_element(), location[0],location[1]).click().perform()
            time.sleep(1)

    def login(self):
        """
        点击验证按钮
        :return: None
        """
        button = self.wait.until(EC.element_to_be_clickable((By.ID, 'J-login')))
        button.click()

    def click(self):
        """
        破解入口
        :return: None
        """
        #1、 切换密码登陆，输入账号密码
        self.open()
        #2、 获取验证码图片
        image = self.get_touclick_image()
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')
        # 识别验证码
        result = self.chaojiying.PostPic(bytes_array.getvalue(), CHAOJIYING_KIND)
        print(result)
        #解析返回结果，得到坐标
        locations = self.get_points(result)
        #根据坐标点击
        self.touch_click_words(locations)
        #点击登陆
        self.login()
        #判断是否登陆成功，登陆成功会有搜索框
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, 'search-input')),'登陆失败')
        except TimeoutException as e:
            print(e)
            self.click()




if __name__ == '__main__':
    touch = touch()
    touch.click()