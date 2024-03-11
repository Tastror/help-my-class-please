import os
import time
import win32gui
import win32con
import win32process
import hmcp_lib as he


def open_awake(class_name, title, path: str, sep_time=4, wait_time=0) -> int:
    open_exe(path)
    time.sleep(sep_time)
    hwnd = win32gui.FindWindow(class_name, title)
    code = awake(hwnd)
    time.sleep(wait_time)
    return code


def open_exe(path: str) -> None:
    if path and os.path.exists(path):
        if os.path.isfile(path):
            try:
                win32process.CreateProcess(
                    str(path), '', None, None, 0, win32process.CREATE_NO_WINDOW,
                    None, None, win32process.STARTUPINFO()
                )
            except Exception as e:
                print("\033[1;31m" + str(e) + "\033[0m")
        else:
            os.startfile(str(path))
    else:
        print('\033[1;31m无法打开软件目录，请检查配置文件．\033[0m')


def awake(hwnd: int) -> int:
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
        win32gui.SetForegroundWindow(hwnd)
        return he.OK
    except Exception as e:
        print(e)
        return he.ERROR
