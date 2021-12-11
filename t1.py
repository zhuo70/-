#!/usr/bin/python3
from interval import Interval
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time
import datetime
import os.path
from io import BytesIO
# 二进制数据的读取操作
from PIL import Image
from selenium.webdriver.support.wait import WebDriverWait
from hashlib import md5
import requests
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
# 配置驱动路径
DRIVER_PATH = '/opt/driver/bin/chromedriver'

CHAOJIYING_USERNAME = 'zhuo90'
CHAOJIYING_PASSWORD = 'lele1725'
CHAOJIYING_SOFT_ID = 893590
CHAOJIYING_KIND = 9103
NAME = "201930921093"
PASSWORD = "lele1725"

class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

class Chaojiying(object):

    def __init__(self, username: object, password: object, soft_id: object) -> object:
        self.username = username
        self.password = md5(password.encode('utf-8')).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def post_pic(self, im, codetype):
        """
       im: 图片字节
       codetype: 题目类型 参考 http://www.chaojiying.com/price.html
       """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def report_error(self, im_id):
        """
       im_id:报错题目的图片ID
       """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


class AutoLogin():
    def __init__(self):
        self.url = 'https://seat.ujn.edu.cn'
        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options )
        self.wait = WebDriverWait(self.driver, 30)
        self.name = NAME
        self.password = PASSWORD
        self.chao = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)
    def start(self):
        self.driver.maximize_window()

    def open(self):
       # time.sleep(1)
        self.driver.get(self.url)
        print("进入网页")
        time.sleep(1)
        # 输入账号
        self.driver.find_element(By.NAME, "username").clear()
        self.driver.find_element(By.NAME, "username").send_keys(self.name)
        # 输入密码
        self.driver.find_element(By.NAME, "password").clear()
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        time.sleep(0.5)
        print(self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div[2]/dl/form/dd[3]/input').get_attribute('value'))
        self.driver.find_element(By.CLASS_NAME, "verifyCode").click()
        time.sleep(0.5)
       # print(self.driver.find_element(By.CLASS_NAME, "verifyCode".text)

    def get_login_element(self):
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "layui-layer-content")))
        element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "layui-layer-content")))
        print('成功获取验证码节点:')
        return element

    def get_position(self):
        element = self.get_login_element()
        time.sleep(0.5)
        location_1 = element.location
        size_1 = element.size
        top, bottom, left, right = location_1['y'], location_1['y'] + size_1['height'], location_1['x'], location_1['x'] + size_1[
            'width']
        top = int(top)
        bottom = int(bottom)
        left = int(left)
        right = int(right)
        return (top, bottom, left, right)

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        img_path = '/root/test/t1/screenshot'
        img_name = time.strftime('screeenshot_%m-%d %H:%M:%S', time.localtime(time.time()))
        img = "%s.png" % os.path.join(img_path, img_name)
        screenshot.save(img)
        return screenshot

    def get_login_image(self, name="captch.png"):
        """
            获取验证码图片
            :return: 图片对象
            """
        top, bottom, left, right = self.get_position()
        print('验证码位置:', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha
 
    def get_points(self, captcha_result):
        """
           #     解析识别结果
           #     :param captcha_result: 识别结果
           #     :return: 转化后的结果
           #     """
        err_no = captcha_result.get('err_no')
        if err_no == 0 :
            groups = captcha_result.get('pic_str').split('|')
            locations = [[int(number) for number in group.split(',')] for group in groups]
            return locations
        else :
            result = self.chao.report_error(im_id=captcha_result.get('pic_id'))
            self.get_points(result)


    def touch_click_words(self, locations):
        """
            点击验证图片
            :param locations: 点击位置
            :return: None
            """
        for location in locations:
            print(location)
            ActionChains(self.driver).move_to_element_with_offset(self.get_login_element(), location[0],
                                                                  location[1]).click().perform()
            time.sleep(1)

    def login_well(self):
        time.sleep(0.5)
        self.driver.find_element(By.CLASS_NAME, "btn1").click()
        time.sleep(0.5)
        print('登录成功')

    def sss(self):
        self.driver.find_element(By.LINK_TEXT, "常用座位").click()
       # time.sleep(0.5)
       # self.driver.find_element("tom = document.getElementById('options_onDate').getElementsByTagName('a')[1].getAttribute('value')"
       # self.driver.execute_script ("aa = document.getElementById('options_onDate').getElementsByTagName('a')[1]")
       # time.sleep(0.5)
       # self.driver.execute_script ("tom =aa.getAttribute('value')")
        time.sleep(1)
        self.driver.execute_script ("document.getElementById('onDate').value = document.getElementById('options_onDate').getElementsByTagName('a')[1].getAttribute('value')")
       # now = datetime.datetime.now().date()
       # tom = now + timedelta(days=1)
       # self.driver.find_element_by_id("onDate").send_keys("2021-12-08")
       # self.driver.execute_script ("document.getElementById('onDate').value = tom")
        time.sleep(0.2)
        self.driver.find_element(By.ID, "seat_9419").click()
        time.sleep(0.2)
        self.driver.find_element(By.CLASS_NAME, "verifyCode").click()
        time.sleep(0.2)       
        print(self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/input').get_attribute('value'))
        time.sleep(0.2)

    def last(self):
        self.driver.find_element(By.LINK_TEXT, "13:00").click()
        time.sleep(0.2)
        self.driver.find_element(By.XPATH, "/html/body/div[5]/div[1]/div[3]/dl/ul/li[4]/a").click()
        now_time = datetime.datetime.now()
        next_year = now_time.date().year
        next_month = now_time.date().month
        next_day = now_time.date().day
        next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 07:00:03", "%Y-%m-%d %H:%M:%S")
        ti = (next_time - now_time).total_seconds()
        print(ti)
       # time.sleep(ti)
        self.driver.find_element(By.ID, "reserveBtn").click()

    def yanzheng(self):
        value = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div[2]/dl/form/dd[3]/input').get_attribute('value')
        n=1
        while True :
                 print('第一次验证开始——%d：'%n)
                 self.driver.switch_to.frame('layui-layer-iframe1')
                 ele=  self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "myCaptcha-image")))
                 self.driver.switch_to.default_content()
                 image = self.get_login_image('/root/test/t1/screenshot/captch.png')
                 bytes_array = BytesIO()
                 image.save(bytes_array, format='PNG')
                 result = self.chao.post_pic(bytes_array.getvalue(), CHAOJIYING_KIND)
                 print(result)
                 locations = self.get_points(result)
                 self.touch_click_words(locations)
                 time.sleep(0.5)
                 value = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div[2]/dl/form/dd[3]/input').get_attribute('value')
                 n=n+1
                 if n==3 :
                     self.save_image(im_path= '/root/test/t1/stop')
                     print("两次未通过第一次验证 ")
                     break
                 if  value=="验证通过" :
                     print('第一次'+value)
                     break
        return value
    def yanzheng_2(self):
        value_2 = self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/input').get_attribute('value')
        n=1
        while True :
                 print('第二次验证开始——%d：'%n)
                 self.driver.switch_to.frame('layui-layer-iframe1')
                 ele=  self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "myCaptcha-image")))
                 self.driver.switch_to.default_content()
                 image = self.get_login_image('/root/test/t1/screenshot/captch2.png')
                 bytes_array = BytesIO()
                 image.save(bytes_array, format='PNG')
                 result = self.chao.post_pic(bytes_array.getvalue(), CHAOJIYING_KIND)
                 print(result)
                 locations = self.get_points(result)
                 self.touch_click_words(locations)
                 time.sleep(1)
                 value_2 = self.driver.find_element_by_xpath('/html/body/div[5]/div[2]/div/input').get_attribute('value')
                 n = n+1
                 if n == 3 :
                     self.save_image(im_path= '/root/test/t1/stop')
                     print("两次未通过第二次验证 ")
                     break
                 if  value_2 =="验证通过" :
                     print('第二次'+value_2)
                     break
        return value_2          
     
    def save_image(self,im_path):
        img_path = im_path
        img_name = time.strftime('%m-%d %H:%M:%S', time.localtime(time.time()))
        img = "%s.png" % os.path.join(img_path, img_name)
        screenshot = self.driver.get_screenshot_as_file(img)
        
if __name__ == "__main__":
    # 设置浏览器
    sys.stdout = Logger('/root/test/t1/t1.log',stream=sys.stdout)
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')  # 无头参数
    options.add_argument('--disable-gpu')
    # 启动浏览器
   # driver = Chrome(executable_path=DRIVER_PATH, options=options)
   # driver.maximize_window()
    autologin = AutoLogin()
    autologin.start()
    print(autologin.driver.get_window_size())
   # scroll_width = 1600
   # scroll_height = 1500
   # autologin.driver.set_window_size(scroll_width, scroll_height)
    
    
    try:
        # 访问页面
        autologin.open()
        scroll_width = 1600
        scroll_height = 1500
        autologin.driver.set_window_size(scroll_width, scroll_height)
        print(autologin.driver.get_window_size())
        value = autologin.yanzheng()
        if value == "验证通过":
             autologin.login_well()
             autologin.sss()
             value_2 = autologin.yanzheng_2()
             if value_2 == "验证通过" :
                    # autologin.driver.execute_script ("document.getElementById('onDate').value = '2021-12-08'")
                     autologin.last()
                    # autologin.save_image('/root/test/t1/img_log')
                     print("预约成功")
             else:
                     autologin.save_image('/root/test/t1/error')
                     print("验证错误2")
        else:
             autologin.save_image('/root/test/t1/error')
             print("验证错误1")
       # autologin.crack()
       # url = 'https://www.jianshu.com/u/a94f887f8776'
       # driver.get(url)
        time.sleep(1)
 
        # 设置截屏整个网页的宽度以及高度
       # scroll_width = 1600
        #scroll_height = 1500
        #driver.set_window_size(scroll_width, scroll_height)
 
        # 保存图片
       # img_path = os.getcwd()
       # img_name = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
       # img = "%s.png" % os.path.join(img_path, img_name)
       # driver.get_screenshot_as_file(img)
 
        # 关闭浏览器
 
    except Exception as e:
        print(e)
    finally:
        autologin.save_image('/root/test/t1/img_log')
        autologin.driver.close()
        autologin.driver.quit()

