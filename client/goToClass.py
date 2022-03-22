import ssl
import time
import urllib3
import requests
import cv2 as cv
import numpy as np
import pyperclip as pc
import pyautogui as pag
from winAPI import open_awake
from selenium import webdriver
from selenium.webdriver.common.by import By
from lockThreads import reserve_browser_driver
from webdriver_manager.chrome import ChromeDriverManager


def print_warning(words: str):
    print("\033[1;33m" + words + "\033[0m")


def print_error(words: str):
    print("\033[1;31m" + words + "\033[0m")


def press(key: str, log="", wait_time=0.0) -> None:
    pag.press(key)
    if log != "":
        print(log)
    time.sleep(wait_time)


def paste(words: str, log="", wait_time=0.0) -> None:
    pc.copy(words)
    pag.hotkey('ctrl', 'v')
    if log != "":
        print(log)
    time.sleep(wait_time)


def clear_paste(words: str, log="", wait_time=0.0) -> None:
    pag.hotkey('ctrl', 'a')
    pag.press('backspace')
    pc.copy(words)
    pag.hotkey('ctrl', 'v')
    if log != "":
        print(log)
    time.sleep(wait_time)


def paste_passwd(words: str, log="", wait_time=0.0) -> None:
    for char in words:
        pag.press(char)
    if log != "":
        print(log)
    time.sleep(wait_time)


def cv_click(template_src: str, width_rate=0.5, height_rate=0.5, log="", wait_time=0.0) -> int:
    template_src_path = "./src/" + template_src + ".png"
    temp = cv.imread(template_src_path)
    w_bias = int(temp.shape[1] * width_rate)
    h_bias = int(temp.shape[0] * height_rate)
    click_list, rep, thr = [], 5, 0
    while len(click_list) == 0 and rep > 0:
        im = pag.screenshot()
        cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
        result: np.ndarray = cv.matchTemplate(cim, temp, cv.TM_SQDIFF)
        cv.normalize(result, result, 0, 1, cv.NORM_MINMAX, -1)
        loc = np.where(result <= thr)
        click_list = [pt for pt in zip(*loc[::-1])]
        rep -= 1
        thr += 1E-12
    if len(click_list) == 0:
        print_warning('"' + log + '"识别失败')
    for pt in click_list:
        if log != "":
            print(log, " [点击 ", (pt[0] + w_bias, pt[1] + h_bias), "]", sep="")
        pag.click(pt[0] + w_bias, pt[1] + h_bias)
    time.sleep(wait_time)
    return len(click_list)


def cv_see(template_src: str, strict=False, wait_time=0.0) -> int:
    template_src_path = "./src/" + template_src + ".png"
    temp = cv.imread(template_src_path)
    click_list, rep, thr = [], 5, 0
    if strict:
        rep = 1
    while len(click_list) == 0 and rep > 0:
        im = pag.screenshot()
        cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
        result: np.ndarray = cv.matchTemplate(cim, temp, cv.TM_SQDIFF)
        cv.normalize(result, result, 0, 1, cv.NORM_MINMAX, -1)
        loc = np.where(result <= thr)
        click_list = [pt for pt in zip(*loc[::-1])]
        rep -= 1
        thr += 1E-12
    time.sleep(wait_time)
    return len(click_list)


class GoToClass:
    def __init__(self, path_dict):
        self.path_dict = path_dict

    def sign_up(self, platform: str, lasting_minutes: int) -> None:
        check_interval = 30
        tick = lasting_minutes * 60 / check_interval
        while tick > 0:
            tick -= 1
            print("检查" + platform + "签到……")
            # 等待书写 cv 的检测内容
            time.sleep(check_interval)

    def go_to_class(self, cla) -> int:

        name = cla.get("name", "<名称未知>")
        platform = cla.get("platform", "")
        detail = cla.get("detail", {})
        time_lasting = cla.get("time_lasting", 100)

        press("space", log="正在唤醒", wait_time=4)
        print("即将进入课堂:", name)

        #
        #  0x01
        #  腾讯会议
        #  使用网页转客户端登录 (url -> client)，或客户端直接登录 (client)
        #
        if platform == "腾讯会议":

            url = detail.get("url", "")
            meeting_id = detail.get("id", "")
            passwd = detail.get("passwd", "")
            myname = detail.get("myname", "")
            auto_close_audio = detail.get("auto_close_audio", False)

            if meeting_id == "" and url == "":
                print_error("加入会议失败：没有网址或会议号")
                return 3

            if meeting_id == "" and url != "":
                try:
                    option = webdriver.ChromeOptions()
                    option.add_argument("--headless")
                    option.add_argument("--disable-notifications")
                    option.add_argument("--disable-popup-blocking")
                    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
                    browser.get(url)
                    meeting_id = browser.find_element(by=By.CSS_SELECTOR, value="#tm-meeting-code").text
                except (ssl.SSLEOFError, urllib3.exceptions.MaxRetryError, requests.exceptions.SSLError):
                    print_error("网络错误，请检查 proxy 是否关闭")
                    return 4

            if meeting_id != "":
                if open_awake(None, "腾讯会议", self.path_dict.get('腾讯会议'), sep_time=4, wait_time=2) != 2:
                    print_error("腾讯会议窗口打开失败！")
                    return 3
                if cv_see('add_meeting', strict=True):
                    cv_click('add_meeting', log="正在点击加入会议", wait_time=1)
                else:
                    pag.hotkey('win', 'tab')
                    time.sleep(1.5)
                    cv_click('wemeet_tab', wait_time=1)
                    cv_click('add_meeting', log="正在点击加入会议", wait_time=1)
                cv_click('meeting_id', 1, 2.2, log="正在点击会议号")
                clear_paste(meeting_id, log="正在输入会议号")
                if myname != "":
                    if cv_click('your_name', 1, 2.2, log="正在点击您的名称") > 0:
                        clear_paste(myname, log="正在输入您的名称")
                if auto_close_audio:
                    pass
                    # 待添加去除麦克风和摄像头
                press("enter", wait_time=1)
                if cv_see("passwd") > 0:
                    if passwd == "":
                        print_warning("加入会议可能不成功：未指定入会密码")
                    else:
                        paste_passwd(passwd, "正在输入入会密码")
                    pag.press("enter")

            print("进入" + name + "课堂操作结束")
            return 2

        #
        #  0x02
        #  腾讯课堂
        #  使用网页直接登录 (url)，或客户端登录并搜索 (client -> index)
        #  不希望支持网页登录并搜索 (url -> index)，
        #
        elif platform == "腾讯课堂":

            using = detail.get("using", "url")
            url = detail.get("url", "")

            if using != "client" and using != "url":
                print_warning("加入方式 using（网页或客户 端）指定有误，正在调整")
                if url == "":
                    print_warning("没有课堂链接，即将使用客户 端")
                    using = "client"
                else:
                    print_warning("找到课堂链接，即将使用客户端")
                    using = "url"

            if using == "client":
                if open_awake(None, "登录", self.path_dict.get('腾讯课堂'), sep_time=4, wait_time=2) != 2:
                    print_error("腾讯课堂窗口打开失败！")
                    return 3
                if cv_see("quick_login", strict=True):
                    cv_click("quick_login", log="正在点击快速登录", wait_time=2)

            if using == "url":
                try:
                    option = webdriver.ChromeOptions()
                    option.add_argument("--disable-notifications")
                    option.add_argument("--disable-popup-blocking")
                    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
                    browser.get(url)
                    time.sleep(1)
                    if cv_see("ke_qq_login", wait_time=1) > 0:
                        print_warning("即将使用QQ登录课堂，请确保你的QQ在线")
                        cv_click("ke_qq_login", 0.6, -0.6, log="正在使用QQ登录课堂")
                    reserve_browser_driver(browser)
                except (ssl.SSLEOFError, urllib3.exceptions.MaxRetryError, requests.exceptions.SSLError):
                    print_error("网络错误，请检查 proxy 是否关闭")
                    return 4

            print("进入" + name + "课堂操作结束")
            # 签到，还未彻底完成
            # threading.Thread(target=self.sign_up(), args=("腾讯课堂", time_lasting), daemon=True).start()
            return 2

        #
        #  0xFF
        #  其他处理
        #
        elif platform == "":
            print_error("未指定任何课程平台，无法自动上课")
            return 3
        else:
            print_error("课程平台输入有误或尚不支持，无法自动上课")
            return 3
