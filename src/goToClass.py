import os
import ssl
import time
import urllib3
import requests
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import hmcp_lib as he


class GoToClass:
    def __init__(self, path_dict):
        self.path_dict = path_dict
        self.check_interval = 20

    def sign_up(self, log: str, lasting_minutes: int) -> None:
        tick = int(lasting_minutes * 60 / self.check_interval)
        while tick > 0:
            tick -= 1
            time_use = time.time()
            he.log.tip(log + "签到检查剩余", tick, "次")
            he.view.click_multiple_possible_images("tencent_ketang_qiandao", "tencent_ketang_qiandao_2", log="签到按键")
            time.sleep(self.check_interval - (time.time() - time_use))

    def detect_qrcode(self, log: str, lasting_minutes: int) -> None:
        tick = int(lasting_minutes * 60 / self.check_interval)
        while tick > 0:
            tick -= 1
            time_use = time.time()
            he.log.tip(log + "二维码检查剩余", tick, "次")
            he.view.qrcode_detect()
            time.sleep(self.check_interval - (time.time() - time_use))

    def go_to_class(self, cla) -> int:

        name = cla.get("name")
        time_lasting = cla.get("time_lasting")
        platform = cla.setdefault("platform", "")
        detail = cla.setdefault("detail", {})

        he.log.enter()
        he.log.tip("正在唤醒，请等待几秒")
        he.pag.press("home", log="home", wait_time=4)
        he.log.tip("即将进入课堂:", name)

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
                he.log.error("加入会议失败：没有网址或会议号")
                return 3

            if meeting_id == "" and url != "":
                try:
                    he.log.tip("正在打开网页")
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
                    he.log.error("网络错误，请检查 proxy 是否关闭")
                    return 4

            if meeting_id != "":
                he.log.tip("正在打开腾讯会议窗口，请等待几秒")
                if he.winAPI.open_awake(None, "腾讯会议", self.path_dict.get('腾讯会议'), sep_time=5, wait_time=5) != he.OK:
                    he.log.warning("腾讯会议窗口可能打开失败")
                he.log.tip("正在尝试加入会议")
                if he.view.see('add_meeting', log="加入会议") != he.OK:
                    he.log.tip("进入任务栏查找腾讯会议")
                    he.pag.hotkey('win', 'tab', log="win + tab", wait_time=1.5)
                    if he.view.click('wemeet_tab', log="腾讯会议标志图", wait_time=1) != he.OK:
                        he.view.click('wemeet_tab2', log="腾讯会议标志图(2)", wait_time=1)
                # 断网等待 1
                rep = 0
                while he.view.see('wireless_board', log="共享屏幕", threshold=0.85) != he.OK and rep < 10:
                    time.sleep(1)
                    rep += 1
                he.view.click('add_meeting', log="加入会议", wait_time=0.1)
                # 断网等待 2
                rep = 0
                while he.view.see('meeting_id', log="会议号", threshold=0.85) != he.OK and rep < 10:
                    time.sleep(1)
                    rep += 1
                    he.view.click('add_meeting', log="加入会议", wait_time=1)
                he.view.click('meeting_id', 1, 2.5, log="会议号")
                he.pag.clear_paste(meeting_id, log="会议号")
                if myname != "":
                    if he.view.click('your_name', 1, 2.5, log="您的名称") == he.OK:
                        he.pag.clear_paste(myname, log="您的名称")
                if auto_close_audio:
                    if he.view.compare("camera_closed", "camera_open", log="摄像头是否关闭") == 1:
                        he.view.click("camera_open", width_offset_rate=0.1, log="摄像头关闭键", wait_time=0.5)
                    if he.view.compare("microphone_closed", "microphone_open", log="麦克风是否关闭") == 1:
                        he.view.click("microphone_open", width_offset_rate=0.1, log="麦克风关闭键", wait_time=0.5)
                he.view.click("add_meeting_bar", log="加入会议", wait_time=4)
                if he.view.see("passwd", log="入会密码", threshold=0.85) == he.OK:
                    if passwd == "":
                        he.log.warning("加入会议可能不成功：未指定入会密码")
                    else:
                        he.pag.paste_passwd(passwd, log="入会密码")
                    he.pag.press("enter")

            he.log.tip("进入" + name + "课堂操作结束")
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
                he.log.warning("加入方式 using（网页或客户端）指定有误，正在调整")
                if url == "":
                    he.log.warning("没有课堂链接，即将使用客户端")
                    using = "client"
                else:
                    he.log.warning("找到课堂链接，即将使用客户端")
                    using = "url"

            if using == "client":
                he.log.tip("正在打开客户端")
                if he.winAPI.open_awake(None, "登录", self.path_dict.get('腾讯课堂'), sep_time=4, wait_time=2) != he.OK:
                    he.log.error("腾讯课堂窗口打开失败")
                    return 3
                if he.view.see("quick_login", log="快速登录", threshold=0.8) == he.OK:
                    he.view.click("quick_login", log="快速登录", wait_time=2)

            if using == "url":
                try:
                    he.log.tip("正在打开网页")
                    option = webdriver.ChromeOptions()
                    os.environ['WDM_LOG_LEVEL'] = '0'
                    option.add_argument('--log-level=3')
                    option.add_argument("--disable-logging")
                    option.add_argument("--disable-notifications")
                    option.add_argument("--disable-popup-blocking")
                    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
                    browser.get(url)
                    time.sleep(1)
                    he.log.warning("即将使用QQ登录课堂，请确保你的QQ在线")
                    rep = 0
                    while he.view.see("ke_qq_login", log="QQ快速登陆", wait_time=1) != he.OK and rep < 10:
                        time.sleep(1)
                        rep += 1
                    he.view.click("ke_qq_login", 0.6, -0.6, log="QQ快速登陆")
                    he.thread.reserve_browser_driver(browser)
                except (ssl.SSLEOFError, urllib3.exceptions.MaxRetryError, requests.exceptions.SSLError):
                    he.log.error("网络错误，请检查您的网络是否存在问题")
                    return 4

            he.log.tip("进入", name, "课堂操作结束")
            threading.Thread(target=self.sign_up, args=("腾讯课堂", time_lasting), daemon=True).start()
            threading.Thread(target=self.detect_qrcode, args=("腾讯课堂", time_lasting), daemon=True).start()
            return 2

        #
        #  0xFF
        #  其他处理
        #
        elif platform == "":
            he.log.error("未指定任何课程平台，无法自动上课")
            return 3
        else:
            he.log.error("课程平台输入有误或尚不支持，无法自动上课")
            return 3
