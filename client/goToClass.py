import os
import ssl
import time
import urllib3
import requests
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from imports import sprint, spag, scv
from imports.swinAPI import open_awake
from imports.sthread import reserve_browser_driver


class GoToClass:
    def __init__(self, path_dict):
        self.path_dict = path_dict
        self.check_interval = 20

    def sign_up(self, log: str, lasting_minutes: int) -> None:
        tick = int(lasting_minutes * 60 / self.check_interval)
        while tick > 0:
            tick -= 1
            time_use = time.time()
            sprint.tip(log + "签到检查剩余", tick, "次")
            scv.click_list("tencent_ketang_qiandao", "tencent_ketang_qiandao_2", log="签到按键")
            time.sleep(self.check_interval - (time.time() - time_use))

    def detect_qrcode(self, log: str, lasting_minutes: int) -> None:
        tick = int(lasting_minutes * 60 / self.check_interval)
        while tick > 0:
            tick -= 1
            time_use = time.time()
            sprint.tip(log + "二维码检查剩余", tick, "次")
            scv.qrcode_detect()
            time.sleep(self.check_interval - (time.time() - time_use))

    def go_to_class(self, cla) -> int:

        name = cla.get("name")
        time_lasting = cla.get("time_lasting")
        platform = cla.setdefault("platform", "")
        detail = cla.setdefault("detail", {})

        sprint.enter()
        sprint.tip("正在唤醒，请等待几秒")
        spag.press("home", log="home", wait_time=4)
        sprint.tip("即将进入课堂:", name)

        #
        #  0x01
        #  腾讯会议
        #  使用网页转客户端登录 (url -> client)，或客户端直接登录 (client)
        #
        if platform == "腾讯会议":

            url = detail.setdefault("url", "")
            meeting_id = detail.setdefault("id", "")
            passwd = detail.setdefault("passwd", "")
            myname = detail.setdefault("myname", "")
            auto_close_audio = detail.setdefault("auto_close_audio", True)

            if meeting_id == "" and url == "":
                sprint.error("加入会议失败：没有网址或会议号")
                return 3

            if meeting_id == "" and url != "":
                try:
                    sprint.tip("正在打开网页")
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
                    sprint.error("网络错误，请检查 proxy 是否关闭")
                    return 4

            if meeting_id != "":
                sprint.tip("正在打开腾讯会议窗口，请等待几秒")
                if open_awake(None, "腾讯会议", self.path_dict.get('腾讯会议'), sep_time=5, wait_time=5) != 2:
                    sprint.warning("腾讯会议窗口可能打开失败")
                sprint.tip("正在尝试加入会议")
                if scv.see('add_meeting', log="加入会议") != 2:
                    sprint.tip("进入任务栏查找腾讯会议")
                    spag.hotkey('win', 'tab', log="win + tab", wait_time=1.5)
                    if scv.click('wemeet_tab', log="腾讯会议标志图", wait_time=1) != 2:
                        scv.click('wemeet_tab2', log="腾讯会议标志图(2)", wait_time=1)
                # 断网等待 1
                rep = 0
                while scv.see('wireless_board', log="无线投屏", threshold=0.85) != 2 and rep < 20:
                    time.sleep(1)
                    rep += 1
                scv.click('add_meeting', log="加入会议", wait_time=1)
                # 断网等待 2
                rep = 0
                while scv.see('meeting_id', log="会议号", threshold=0.85) != 2 and rep < 60:
                    time.sleep(1)
                    rep += 1
                    scv.click('add_meeting', log="加入会议", wait_time=1)
                scv.click('meeting_id', 1, 2.5, log="会议号")
                spag.clear_paste(meeting_id, log="会议号")
                if myname != "":
                    if scv.click('your_name', 1, 2.5, log="您的名称") == 2:
                        spag.clear_paste(myname, log="您的名称")
                if auto_close_audio:
                    if scv.compare("camera_closed", "camera_open", log="摄像头是否关闭") == 1:
                        scv.click("camera_open", width_rate=0.1, log="摄像头关闭键", wait_time=0.5)
                    if scv.compare("microphone_closed", "microphone_open", log="麦克风是否关闭") == 1:
                        scv.click("microphone_open", width_rate=0.1, log="麦克风关闭键", wait_time=0.5)
                scv.click("add_meeting_bar", log="加入会议", wait_time=4)
                if scv.see("passwd", log="入会密码") == 2:
                    if passwd == "":
                        sprint.warning("加入会议可能不成功：未指定入会密码")
                    else:
                        spag.paste_passwd(passwd, log="入会密码")
                    spag.press("enter")

            sprint.tip("进入" + name + "课堂操作结束")
            threading.Thread(target=self.detect_qrcode, args=("腾讯会议", time_lasting), daemon=True).start()
            return 2

        #
        #  0x02
        #  腾讯课堂
        #  使用网页直接登录 (url)，或客户端登录并搜索 (client -> index)
        #  不希望支持网页登录并搜索 (url -> index)，
        #
        elif platform == "腾讯课堂":

            using = detail.setdefault("using", "url")
            url = detail.setdefault("url", "")

            if using != "client" and using != "url":
                sprint.warning("加入方式 using（网页或客户端）指定有误，正在调整")
                if url == "":
                    sprint.warning("没有课堂链接，即将使用客户端")
                    using = "client"
                else:
                    sprint.warning("找到课堂链接，即将使用客户端")
                    using = "url"

            if using == "client":
                sprint.tip("正在打开客户端")
                if open_awake(None, "登录", self.path_dict.get('腾讯课堂'), sep_time=4, wait_time=2) != 2:
                    sprint.error("腾讯课堂窗口打开失败！")
                    return 3
                if scv.see("quick_login", log="快速登录", threshold=0.8) == 2:
                    scv.click("quick_login", log="快速登录", wait_time=2)

            if using == "url":
                try:
                    sprint.tip("正在打开网页")
                    option = webdriver.ChromeOptions()
                    os.environ['WDM_LOG_LEVEL'] = '0'
                    option.add_argument('--log-level=3')
                    option.add_argument("--disable-logging")
                    option.add_argument("--disable-notifications")
                    option.add_argument("--disable-popup-blocking")
                    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
                    browser.get(url)
                    time.sleep(1)
                    sprint.warning("即将使用QQ登录课堂，请确保你的QQ在线")
                    rep = 0
                    while scv.see("ke_qq_login", log="QQ快速登陆", wait_time=1) != 2 and rep < 20:
                        time.sleep(1)
                        rep += 1
                    scv.click("ke_qq_login", 0.6, -0.6, log="QQ快速登陆")
                    reserve_browser_driver(browser)
                except (ssl.SSLEOFError, urllib3.exceptions.MaxRetryError, requests.exceptions.SSLError):
                    sprint.error("网络错误，请检查 proxy 是否关闭")
                    return 4

            sprint.tip("进入", name, "课堂操作结束")
            threading.Thread(target=self.sign_up, args=("腾讯课堂", time_lasting), daemon=True).start()
            threading.Thread(target=self.detect_qrcode, args=("腾讯课堂", time_lasting), daemon=True).start()
            return 2

        #
        #  0xFF
        #  其他处理
        #
        elif platform == "":
            sprint.error("未指定任何课程平台，无法自动上课")
            return 3
        else:
            sprint.error("课程平台输入有误或尚不支持，无法自动上课")
            return 3
