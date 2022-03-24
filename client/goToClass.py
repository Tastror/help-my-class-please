import os
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


def print_warning(*words: any, sep=" ", end="\n"):
    print("\033[1;33mWARN ", end="")
    print(*words, sep=sep, end=end)
    print("\033[0m", end="")


def print_error(*words: any, sep=" ", end="\n"):
    print("\033[1;31mERROR ", end="")
    print(*words, sep=sep, end=end)
    print("\033[0m", end="")


def print_event(*words: any, sep=" ", end="\n"):
    print("\033[1;36mEVENT ", end="")
    print(*words, sep=sep, end=end)
    print("\033[0m", end="")


def print_tip(*words: any, sep=" ", end="\n"):
    print("TIP ", end="")
    print(*words, sep=sep, end=end)


def press(key: str, *, log="", wait_time=0.5) -> None:
    pag.press(key)
    if log != "": log = "：" + log
    print_event("按键", log, sep="")
    time.sleep(wait_time)


def hotkey(*keys: str, log="", wait_time=0.5) -> None:
    pag.hotkey(*keys)
    if log != "": log = "：" + log
    print_event("快捷键", log, sep="")
    time.sleep(wait_time)


def paste(words: str, *, log="", wait_time=0.5) -> None:
    pc.copy(words)
    pag.hotkey('ctrl', 'v')
    if log != "": log = "：" + log
    print_event("输入", log, sep="")
    time.sleep(wait_time)


def clear_paste(words: str, *, log="", wait_time=0.5) -> None:
    pag.hotkey('ctrl', 'a')
    pag.press('backspace')
    pc.copy(words)
    pag.hotkey('ctrl', 'v')
    if log != "": log = "：" + log
    print_event("清空并输入", log, sep="")
    time.sleep(wait_time)


def paste_passwd(words: str, *, log="", wait_time=0.5) -> None:
    for char in words:
        pag.press(char)
    if log != "": log = "：" + log
    print_event("密码输入", log, sep="")
    time.sleep(wait_time)


def cv_detect_single(target: np.ndarray, template_img: np.ndarray) -> any:
    result: np.ndarray = cv.matchTemplate(target, template_img, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    return max_loc, max_val


def cv_detect_all_size(target: np.ndarray, template_img: np.ndarray) -> any:
    res_val, res_loc = 0, None
    for i in range(-5, 6):  # 75% ~ 125%，如果仍然不行可以自行调整范围
        new_temp = cv.resize(template_img, None, fx=1+i/20, fy=1+i/20)
        result: np.ndarray = cv.matchTemplate(target, new_temp, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val > res_val:
            res_val, res_loc = max_val, max_loc
    return res_loc, res_val


def cv_click(template_src: str, width_rate=0.5, height_rate=0.5, *,
             threshold=0.6, log="", wait_time=0.5, all_size=True) -> int:
    if log != "": log = '"' + log + '" '
    template_src_path = "./src/" + template_src + ".png"
    temp = cv.imread(template_src_path)
    im = pag.screenshot()
    cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    if all_size:
        click_point, max_val = cv_detect_all_size(cim, temp)
    else:
        click_point, max_val = cv_detect_single(cim, temp)
    if threshold is not None and max_val < threshold:
        print_warning('图像点击：', log, ('未识别，识别度为 %.3f' % max_val), ('，要求达到 %.3f' % threshold), sep="")
        time.sleep(wait_time)
        return 3
    else:
        w_bias = int(temp.shape[1] * width_rate)
        h_bias = int(temp.shape[0] * height_rate)
        print_event('图像点击：', log, ('识别成功，识别度为 %.3f' % max_val), ' [点击 ',
                    (click_point[0] + w_bias, click_point[1] + h_bias), "]", sep="")
        pag.click(click_point[0] + w_bias, click_point[1] + h_bias)
        time.sleep(wait_time)
        return 2


def cv_see(template_src: str, *, threshold=0.85, log="", wait_time=0.5, all_size=True) -> int:
    if log != "": log = '"' + log + '" '
    template_src_path = "./src/" + template_src + ".png"
    temp = cv.imread(template_src_path)
    im = pag.screenshot()
    cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    if all_size:
        click_point, max_val = cv_detect_all_size(cim, temp)
    else:
        click_point, max_val = cv_detect_single(cim, temp)
    if threshold is not None and max_val < threshold:
        print_warning('图像检测：', log, ('未识别，识别度为 %.3f' % max_val), ('，要求达到 %.3f' % threshold), sep="")
        time.sleep(wait_time)
        return 3
    else:
        print_event('图像检测：', log, ('识别成功，识别度为 %.3f' % max_val), ' [检测点 ',
                    (click_point[0], click_point[1]), "]", sep="")
        time.sleep(wait_time)
        return 2


def cv_compare(*template_src: str, log="", wait_time=0.5, all_size=True) -> int:
    if log != "": log = '"' + log + '" '
    im = pag.screenshot()
    cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    ans = []
    for temp in template_src:
        template_src_path = "./src/" + temp + ".png"
        template_img = cv.imread(template_src_path)
        max_loc, max_val = cv_detect_all_size(cim, template_img)
        ans.append(max_val)
    print_event('图像对比：', log, "对比列表 ", ans, sep="")
    time.sleep(wait_time)
    return ans.index(max(ans))


class GoToClass:
    def __init__(self, path_dict):
        self.path_dict = path_dict

    def sign_up(self, platform: str, lasting_minutes: int) -> None:
        check_interval = 30
        tick = lasting_minutes * 60 / check_interval
        while tick > 0:
            tick -= 1
            print_tip("检查" + platform + "签到……")
            # 等待书写 cv 的检测内容
            time.sleep(check_interval)

    def go_to_class(self, cla) -> int:

        name = cla.get("name", "<名称未知>")
        platform = cla.get("platform", "")
        detail = cla.get("detail", {})
        time_lasting = cla.get("time_lasting", 100)

        print()
        print_tip("正在唤醒，请等待几秒")
        press("home", log="home", wait_time=4)
        print_tip("即将进入课堂:", name)

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
            auto_close_audio = detail.get("auto_close_audio", True)

            if meeting_id == "" and url == "":
                print_error("加入会议失败：没有网址或会议号")
                return 3

            if meeting_id == "" and url != "":
                try:
                    print_tip("正在打开网页")
                    option = webdriver.ChromeOptions()
                    os.environ['WDM_LOG_LEVEL'] = '0'
                    option.add_argument("--headless")
                    option.add_argument('--log-level=3')
                    option.add_argument("--disable-logging")
                    option.add_argument("--disable-notifications")
                    option.add_argument("--disable-popup-blocking")
                    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
                    browser.get(url)
                    meeting_id = browser.find_element(by=By.CSS_SELECTOR, value="#tm-meeting-code").text
                except (ssl.SSLEOFError, urllib3.exceptions.MaxRetryError, requests.exceptions.SSLError):
                    print_error("网络错误，请检查 proxy 是否关闭")
                    return 4

            if meeting_id != "":
                print_tip("正在打开腾讯会议窗口，请等待几秒")
                if open_awake(None, "腾讯会议", self.path_dict.get('腾讯会议'), sep_time=5, wait_time=5) != 2:
                    print_warning("腾讯会议窗口可能打开失败")
                print_tip("正在尝试加入会议")
                if cv_see('add_meeting', log="加入会议") != 2:
                    print_tip("进入任务栏查找腾讯会议")
                    hotkey('win', 'tab', log="win + tab", wait_time=1.5)
                    if cv_click('wemeet_tab', log="腾讯会议标志图", wait_time=1) != 2:
                        cv_click('wemeet_tab2', log="腾讯会议标志图(2)", wait_time=1)
                # 断网等待 1
                rep = 0
                while cv_see('wireless_board', log="无线投屏", threshold=0.85) != 2 and rep < 20:
                    time.sleep(1)
                    rep += 1
                cv_click('add_meeting', log="加入会议", wait_time=1)
                # 断网等待 2
                rep = 0
                while cv_see('meeting_id', log="会议号", threshold=0.85) != 2 and rep < 60:
                    time.sleep(1)
                    rep += 1
                    cv_click('add_meeting', log="加入会议", wait_time=1)
                cv_click('meeting_id', 1, 2.5, log="会议号")
                clear_paste(meeting_id, log="会议号")
                if myname != "":
                    if cv_click('your_name', 1, 2.5, log="您的名称") == 2:
                        clear_paste(myname, log="您的名称")
                if auto_close_audio:
                    if cv_compare("camera_closed", "camera_open", log="摄像头是否关闭") == 1:
                        cv_click("camera_open", width_rate=0.1, log="摄像头关闭键", wait_time=0.5)
                    if cv_compare("microphone_closed", "microphone_open", log="麦克风是否关闭") == 1:
                        cv_click("microphone_open", width_rate=0.1, log="麦克风关闭键", wait_time=0.5)
                cv_click("add_meeting_bar", log="加入会议", wait_time=4)
                if cv_see("passwd", log="入会密码") == 2:
                    if passwd == "":
                        print_warning("加入会议可能不成功：未指定入会密码")
                    else:
                        paste_passwd(passwd, log="入会密码")
                    press("enter")

            print_tip("进入" + name + "课堂操作结束")
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
                print_warning("加入方式 using（网页或客户端）指定有误，正在调整")
                if url == "":
                    print_warning("没有课堂链接，即将使用客户端")
                    using = "client"
                else:
                    print_warning("找到课堂链接，即将使用客户端")
                    using = "url"

            if using == "client":
                print_tip("正在打开客户端")
                if open_awake(None, "登录", self.path_dict.get('腾讯课堂'), sep_time=4, wait_time=2) != 2:
                    print_error("腾讯课堂窗口打开失败！")
                    return 3
                if cv_see("quick_login", log="快速登录", threshold=0.8) == 2:
                    cv_click("quick_login", log="快速登录", wait_time=2)

            if using == "url":
                try:
                    print_tip("正在打开网页")
                    option = webdriver.ChromeOptions()
                    os.environ['WDM_LOG_LEVEL'] = '0'
                    option.add_argument('--log-level=3')
                    option.add_argument("--disable-logging")
                    option.add_argument("--disable-notifications")
                    option.add_argument("--disable-popup-blocking")
                    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
                    browser.get(url)
                    time.sleep(1)
                    print_warning("即将使用QQ登录课堂，请确保你的QQ在线")
                    rep = 0
                    while cv_see("ke_qq_login", log="QQ快速登陆", wait_time=1) == 2 and rep < 20:
                        time.sleep(1)
                        rep += 1
                    cv_click("ke_qq_login", 0.6, -0.6, log="QQ快速登陆")
                    reserve_browser_driver(browser)
                except (ssl.SSLEOFError, urllib3.exceptions.MaxRetryError, requests.exceptions.SSLError):
                    print_error("网络错误，请检查 proxy 是否关闭")
                    return 4

            print_tip("进入", name, "课堂操作结束")
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
