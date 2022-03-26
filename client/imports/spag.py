import time
import pyperclip as pc
import pyautogui as pag

from imports import sprint


def press(key: str, *, log="", wait_time=0.5) -> None:
    pag.press(key)
    if log != "": log = "：" + log
    sprint.event("按键", log, sep="")
    time.sleep(wait_time)


def hotkey(*keys: str, log="", wait_time=0.5) -> None:
    pag.hotkey(*keys)
    if log != "": log = "：" + log
    sprint.event("快捷键", log, sep="")
    time.sleep(wait_time)


def paste(words: str, *, log="", wait_time=0.5) -> None:
    pc.copy(words)
    pag.hotkey('ctrl', 'v')
    if log != "": log = "：" + log
    sprint.event("输入", log, sep="")
    time.sleep(wait_time)


def clear_paste(words: str, *, log="", wait_time=0.5) -> None:
    pag.hotkey('ctrl', 'a')
    pag.press('backspace')
    pc.copy(words)
    pag.hotkey('ctrl', 'v')
    if log != "": log = "：" + log
    sprint.event("清空并输入", log, sep="")
    time.sleep(wait_time)


def paste_passwd(words: str, *, log="", wait_time=0.5) -> None:
    for char in words:
        pag.press(char)
    if log != "": log = "：" + log
    sprint.event("密码输入", log, sep="")
    time.sleep(wait_time)


def screenshot():
    return pag.screenshot()


def click(x=None, y=None, clicks=1, interval=0.0, duration=0.0, logScreenshot=None, _pause=True):
    pag.click(x=x, y=y, clicks=clicks, interval=interval, duration=duration,
              logScreenshot=logScreenshot, _pause=_pause)
