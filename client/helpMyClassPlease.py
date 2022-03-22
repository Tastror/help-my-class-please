import re
import sys
import json
import time
import ssl
import urllib3
import requests
import threading
import cv2 as cv
import numpy as np
import pyperclip as pc
import pyautogui as pag
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def series_func(func_list: list) -> None:
    if len(func_list) == 0:
        return
    for i in func_list:
        i.start()
        i.join()
    return


class lock_threads:
    def __init__(self) -> None:
        self.busy = False
        self.working = None
        self.buff_list = []
        self.start_list = []

    def create(self, group=None, target=None, name=None,
               args=(), kwargs=None, *, daemon=None) -> None:
        s = threading.Thread(group, target, name, args, kwargs, daemon=daemon)
        self.buff_list.append(s)

    def start_next(self) -> None:
        if len(self.buff_list) > 0:
            self.start_list.append(self.buff_list.pop(0))

    def normal_fresh(self) -> None:
        if self.working is None or not self.working.is_alive():
            self.busy = False
        if not self.busy and len(self.start_list) > 0:
            self.working = self.start_list.pop(0)
            self.working.start()
            self.busy = True

    def start_all(self) -> None:
        all_list = self.start_list + self.buff_list
        threading.Thread(target=series_func, args=(all_list,), daemon=True).start()
        self.start_list, self.buff_list = [], []


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
    click_list, rep, thr = [], 10, 0
    while len(click_list) == 0 and rep > 0:
        im = pag.screenshot()
        cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
        result: np.ndarray = cv.matchTemplate(cim, temp, cv.TM_SQDIFF)
        cv.normalize(result, result, 0, 1, cv.NORM_MINMAX, -1)
        loc = np.where(result <= thr)
        click_list = [pt for pt in zip(*loc[::-1])]
        # print(thr, click_list)
        rep -= 1
        thr += 1E-10
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
    click_list, rep, thr = [], 10, 0
    if strict:
        rep = 1
    while len(click_list) == 0 and rep > 0:
        im = pag.screenshot()
        cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
        result: np.ndarray = cv.matchTemplate(cim, temp, cv.TM_SQDIFF)
        cv.normalize(result, result, 0, 1, cv.NORM_MINMAX, -1)
        loc = np.where(result <= thr)
        click_list = [pt for pt in zip(*loc[::-1])]
        # print(thr, click_list)
        rep -= 1
        thr += 1E-10
    time.sleep(wait_time)
    return len(click_list)


def sign_up(platform: str, lasting_minutes: int) -> None:
    check_interval = 30
    tick = lasting_minutes * 60 / check_interval
    while tick > 0:
        tick -= 1
        print("检查" + platform + "签到……")
        # 等待书写 cv 的检测内容
        time.sleep(check_interval)


def go_to_class(cla) -> int:
    name = cla.get("name", "<名称未知>")
    print("即将进入课堂:", name)
    platform = cla.get("platform", "")
    detail = cla.get("detail", {})
    press("space", log="正在唤醒", wait_time=3)

    if platform == "腾讯会议":
        url = detail.get("url", "")
        meeting_id = detail.get("id", "")
        passwd = detail.get("passwd", "")
        myname = detail.get("myname", "")
        auto_close_audio = detail.get("auto_close_audio", False)
        browser = None
        if url == "" and meeting_id == "":
            print_error("加入会议失败：没有网址或会议号")
            return 3
        elif url != "":
            try:
                option = webdriver.ChromeOptions()
                option.add_argument("--disable-notifications")
                option.add_argument("--disable-popup-blocking")
                browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
                browser.get(url)
            except (ssl.SSLEOFError, urllib3.exceptions.MaxRetryError, requests.exceptions.SSLError):
                print_error("网络错误，请检查 proxy 是否关闭")
                browser = None
                if meeting_id == "":
                    return 4
        if browser is not None:
            browser.find_element_by_css_selector("#mpJoinBtnCtrl").click()
            time.sleep(0.5)
            if cv_see("open_from_url") > 0:
                cv_click("open_from_url", log="正在跳转链接", wait_time=5)
            else:
                time.sleep(5)
            pag.hotkey('win', 'tab'), time.sleep(1)
            cv_click("awake_from_url", wait_time=1)
            if cv_see("passwd_from_url") > 0:
                if passwd == "":
                    print_warning("加入会议可能不成功：未指定入会密码")
                else:
                    cv_click("passwd_from_url", log="正在点击入会密码")
                    paste_passwd(passwd, "正在输入入会密码")
            if myname != "":
                if cv_click('your_name_from_url', 1, 2.2, log="正在点击入会名称") > 0:
                    clear_paste(myname, log="正在输入入会名称")
            pag.press("enter")
        else:
            press("win", log="正在搜索并打开腾讯会议", wait_time=0.5)
            paste("腾讯会议", wait_time=0.5)
            press("enter", wait_time=5)
            if not cv_see('add_meeting', strict=True):
                pag.hotkey('win', 'tab'), time.sleep(1)
                cv_click("awake", wait_time=1)
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

    elif platform == "腾讯课堂":
        url = detail.get("url", "")
        time_lasting = detail.get("time_lasting", "100")
        if url == "":
            print_error("加入课堂失败：没有课堂网址")
            return 3
        else:
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
            except (ssl.SSLEOFError, urllib3.exceptions.MaxRetryError, requests.exceptions.SSLError):
                print_error("网络错误，请检查 proxy 是否关闭")
                return 4
        print("进入" + name + "课堂操作结束")
        # 签到，还未彻底完成
        # threading.Thread(target=sign_up, args=("腾讯课堂", time_lasting), daemon=True).start()
        return 2

    elif platform == "":
        print_error("未指定任何课程平台，无法自动上课")
        return 3

    else:
        print_error("课程平台输入有误或尚不支持，无法自动上课")
        return 3


class HelpMyClassPlease:
    def __init__(self) -> None:
        self.config = []
        self.today_list = []
        self.sleep_time = 60

    def init(self, file_name) -> None:
        self.read_config(file_name)
        self.today_list = [i for i in range(len(self.config))]
        print("\033[1;35mWarning: 如果开启 proxy，网页功能可能无法正常启动，请检查后再开启本程序\033[0m")
        print()

    def read_config(self, file_name) -> None:
        self.config = json.load(open(file_name, 'r', encoding='utf-8'))
        if len(self.config) > 0:
            print("\033[1;32m课程已从", file_name, "中导入\033[0m")

    def run(self) -> None:
        old_day = 0
        lck_threads = lock_threads()
        use_test, sleep_time, weekday_for_test, time_for_test = False, 10, 1, 499  # 禁用测试请注释将 use_test 置为 False
        if use_test:
            print_warning("Attention: 当前为测试用例，时间流速与平常会有差异。测试参数 "
                          + str((sleep_time, weekday_for_test, time_for_test)) + "\n")
        while True:
            now_time = time.localtime(time.time())
            if now_time.tm_mday != old_day:
                old_day = now_time.tm_mday
                self.today_list = [i for i in range(len(self.config))]
                print("\033[1;36ma new day begins\033[0m")
            print("\033[1;34mheart beat\033[0m")
            now_weekday = now_time.tm_wday + 1
            now_time = now_time.tm_hour * 60 + now_time.tm_min
            if use_test:  # 给定时间测试
                self.sleep_time, now_weekday, now_time, time_for_test \
                    = sleep_time, weekday_for_test, time_for_test, time_for_test + 1
            print("now weekday: ", now_weekday, ", now time: ", now_time // 60, ":", ("%02d" % (now_time % 60)), sep="")
            run_id_list = []
            for i in self.today_list.copy():
                start_time = re.split("[:：.]", self.config[i].get("time", "0:0"))
                start_weekday = self.config[i].get("weekday", [0])
                time_range = self.config[i].get("time_range", [-10, 10])
                pre_time = int(start_time[0]) * 60 + int(start_time[1])
                # print("id:", i, "weekday:", start_weekday, "time:", pre_time, "time_range:", time_range)
                if now_weekday in start_weekday and time_range[0] <= (now_time - pre_time) <= time_range[1]:
                    print("[class chosen] id: ", i, ", weekday: ", start_weekday,
                          ", time: ", pre_time // 60, ":", ("%02d" % (pre_time % 60)), sep="")
                    run_id_list.append(i)
                    self.today_list.remove(i)
            for i in run_id_list:
                lck_threads.create(target=go_to_class, args=(self.config[i],), daemon=True)
            lck_threads.start_all()
            time.sleep(self.sleep_time)
            print()


if __name__ == "__main__":
    hmcp = HelpMyClassPlease()
    if len(sys.argv) > 1:
        hmcp.init(sys.argv[1])
    else:
        hmcp.init("./class.json")
    hmcp.run()
