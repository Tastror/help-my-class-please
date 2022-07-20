import os
import time
import cv2 as cv
import numpy as np

from imports import sprint, spag


def _get_img_path(path_section: str) -> str:
    return "./img/" + path_section + ".png"


def _get_qrcode_path(path_section: str) -> str:
    folder = os.path.exists("../data")
    if not folder: os.mkdir("../data")
    folder = os.path.exists("../data/qrcodes")
    if not folder: os.mkdir("../data/qrcodes")
    return "../data/qrcodes/" + path_section + ".png"


def detect_single(target: np.ndarray, template_img: np.ndarray) -> any:
    result: np.ndarray = cv.matchTemplate(target, template_img, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    return max_loc, max_val


def detect_all_size(target: np.ndarray, template_img: np.ndarray) -> any:
    res_val, res_loc = 0, None
    for i in range(-5, 6):  # 75% ~ 125%，如果仍然不行可以自行调整范围
        new_temp = cv.resize(template_img, None, fx=1+i/20, fy=1+i/20)
        result: np.ndarray = cv.matchTemplate(target, new_temp, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val > res_val:
            res_val, res_loc = max_val, max_loc
    return res_loc, res_val


def click(template_src: str, width_rate=0.5, height_rate=0.5, *,
          threshold=0.6, log="", wait_time=0.5, all_size=True) -> int:
    if log != "": log = '"' + log + '" '
    template_src_path = _get_img_path(template_src)
    temp = cv.imread(template_src_path)
    im = spag.screenshot()
    cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    if all_size:
        click_point, max_val = detect_all_size(cim, temp)
    else:
        click_point, max_val = detect_single(cim, temp)
    if threshold is not None and max_val < threshold:
        sprint.warning('图像点击：', log, ('未识别，识别度为 %.3f' % max_val), ('，要求达到 %.3f' % threshold), sep="")
        time.sleep(wait_time)
        return 3
    else:
        w_bias = int(temp.shape[1] * width_rate)
        h_bias = int(temp.shape[0] * height_rate)
        sprint.event('图像点击：', log, ('识别成功，识别度为 %.3f' % max_val), ' [点击 ',
                     (click_point[0] + w_bias, click_point[1] + h_bias), "]", sep="")
        spag.click(click_point[0] + w_bias, click_point[1] + h_bias)
        time.sleep(wait_time)
        return 2


def see(template_src: str, *, threshold=0.85, log="", wait_time=0.5, all_size=True) -> int:
    if log != "": log = '"' + log + '" '
    template_src_path = _get_img_path(template_src)
    temp = cv.imread(template_src_path)
    im = spag.screenshot()
    cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    if all_size:
        click_point, max_val = detect_all_size(cim, temp)
    else:
        click_point, max_val = detect_single(cim, temp)
    if threshold is not None and max_val < threshold:
        sprint.warning('图像检测：', log, ('未识别，识别度为 %.3f' % max_val), ('，要求达到 %.3f' % threshold), sep="")
        time.sleep(wait_time)
        return 3
    else:
        sprint.event('图像检测：', log, ('识别成功，识别度为 %.3f' % max_val), ' [检测点 ',
                     (click_point[0], click_point[1]), "]", sep="")
        time.sleep(wait_time)
        return 2


def click_list(*template_src: str, width_rate=0.5, height_rate=0.5,
               threshold=0.6, log="", wait_time=0.5, all_size=True) -> int:
    if log != "": log = '"' + log + '" '
    im = spag.screenshot()
    cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    temp_n, click_point_n, max_val_n = None, [0, 0], 0
    for temp in template_src:
        template_src_path = _get_img_path(temp)
        temp = cv.imread(template_src_path)
        if all_size:
            click_point, max_val = detect_all_size(cim, temp)
        else:
            click_point, max_val = detect_single(cim, temp)
        if max_val > max_val_n:
            temp_n = temp
            click_point_n = click_point
            max_val_n = max_val
    if threshold is not None and max_val_n < threshold:
        sprint.warning('图像列点击：', log, ('未识别，最高识别度为 %.3f' % max_val_n), ('，要求达到 %.3f' % threshold), sep="")
        time.sleep(wait_time)
        return 3
    else:
        w_bias = int(temp_n.shape[1] * width_rate)
        h_bias = int(temp_n.shape[0] * height_rate)
        sprint.event('图像列点击：', log, ('识别成功，最高识别度为 %.3f' % max_val_n), ' [点击 ',
                     (click_point_n[0] + w_bias, click_point_n[1] + h_bias), "]", sep="")
        spag.click(click_point_n[0] + w_bias, click_point_n[1] + h_bias)
        time.sleep(wait_time)
        return 2


def compare(*template_src: str, log="", wait_time=0.5, all_size=True) -> int:
    if log != "": log = '"' + log + '" '
    im = spag.screenshot()
    cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)
    ans = []
    for temp in template_src:
        template_src_path = _get_img_path(temp)
        template_img = cv.imread(template_src_path)
        max_loc, max_val = detect_all_size(cim, template_img)
        ans.append(max_val)
    sprint.event('图像对比：', log, "对比列表 ", ans, sep="")
    time.sleep(wait_time)
    return ans.index(max(ans))


def qrcode_detect(*, log="", wait_time=0.0) -> int:
    im = spag.screenshot()
    cim = cv.cvtColor(np.array(im), cv.COLOR_RGB2GRAY)
    qrcode = cv.QRCodeDetector()
    result_detection, transform, straight_qrcode = qrcode.detectAndDecode(cim)
    if transform is not None:
        sprint.event("二维码检测：检测到", log, "二维码，正在保存", sep="")
        cv.imwrite(_get_qrcode_path(str(time.time())), cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR))
        return 2
    else:
        sprint.warning("二维码检测：未检测到", log, "二维码", sep="")
        return 3
