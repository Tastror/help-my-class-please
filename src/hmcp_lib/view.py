import os
import time
import cv2 as cv
import numpy as np
import hmcp_lib as he

last_best_rate = -1

def _get_img_path(path_section: str) -> str:
    return "../resource/img/" + path_section + ".png"


def _get_qrcode_path(path_section: str) -> str:
    folder = os.path.exists("../user-data")
    if not folder: os.mkdir("../user-data")
    folder = os.path.exists("../user-data/qrcodes")
    if not folder: os.mkdir("../user-data/qrcodes")
    return "../user-data/qrcodes/" + path_section + ".png"


def detect_no_zoom(target: np.ndarray, template_img: np.ndarray) -> tuple[tuple[int, int], int]:
    result: np.ndarray = cv.matchTemplate(target, template_img, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    return max_loc, max_val


def detect_zoom_with_rate(target: np.ndarray, template_img: np.ndarray, rate: int) -> tuple[tuple[int, int], int]:
    new_temp = cv.resize(template_img, None, fx=rate, fy=rate)
    result: np.ndarray = cv.matchTemplate(target, new_temp, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    return max_loc, max_val


def detect_zoom_in_and_out(target: np.ndarray, template_img: np.ndarray) -> tuple[tuple[int, int], int, int]:
    res_val, res_loc = 0, (-1, -1)
    for i in range(-5, 6):  # 75% ~ 125%，如果仍然不行可以自行调整范围
        rate = 1 + i / 20
        new_temp = cv.resize(template_img, None, fx=rate, fy=rate)
        result: np.ndarray = cv.matchTemplate(target, new_temp, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val > res_val:
            best_rate, res_val, res_loc = rate, max_val, max_loc
    return res_loc, res_val, best_rate


def click(template_src: str, width_offset_rate=0.5, height_offset_rate=0.5, *,
          threshold=0.6, log="", wait_time=0.0, zoom_in_and_out=True) -> int:
    global last_best_rate
    if log != "": log = '"' + log + '" '
    template_src_path = _get_img_path(template_src)
    template_img = cv.imread(template_src_path)
    origin_screenshot = he.pag.screenshot()
    screenshot = cv.cvtColor(np.array(origin_screenshot), cv.COLOR_RGB2BGR)
    if zoom_in_and_out:
        if last_best_rate > 0 and threshold is not None:
            click_point, max_val = detect_zoom_with_rate(screenshot, template_img, last_best_rate)
            if max_val < threshold:
                click_point, max_val, last_best_rate = detect_zoom_in_and_out(screenshot, template_img)
        else:
            click_point, max_val, last_best_rate = detect_zoom_in_and_out(screenshot, template_img)
    else:
        click_point, max_val = detect_no_zoom(screenshot, template_img)
    if threshold is not None and max_val < threshold:
        he.log.warning('点击：', log, ('未识别，识别度为 %.3f' % max_val), ('，要求达到 %.3f' % threshold), sep="")
        time.sleep(wait_time)
        return he.ERROR
    else:
        w_bias = int(template_img.shape[1] * width_offset_rate)
        h_bias = int(template_img.shape[0] * height_offset_rate)
        he.log.event('点击：', log, ('识别成功，识别度为 %.3f' % max_val), ' [点击 ',
                     (click_point[0] + w_bias, click_point[1] + h_bias), "]", sep="")
        he.pag.click(click_point[0] + w_bias, click_point[1] + h_bias)
        time.sleep(wait_time)
        return he.OK


def see(template_src: str, *, threshold=0.85, log="", wait_time=0.0, zoom_in_and_out=True) -> int:
    global last_best_rate
    if log != "": log = '"' + log + '" '
    template_src_path = _get_img_path(template_src)
    template_img = cv.imread(template_src_path)
    origin_screenshot = he.pag.screenshot()
    screenshot = cv.cvtColor(np.array(origin_screenshot), cv.COLOR_RGB2BGR)
    if zoom_in_and_out:
        if last_best_rate > 0 and threshold is not None:
            click_point, max_val = detect_zoom_with_rate(screenshot, template_img, last_best_rate)
            if max_val < threshold:
                click_point, max_val, last_best_rate = detect_zoom_in_and_out(screenshot, template_img)
        else:
            click_point, max_val, last_best_rate = detect_zoom_in_and_out(screenshot, template_img)
    else:
        click_point, max_val = detect_no_zoom(screenshot, template_img)
    if threshold is not None and max_val < threshold:
        he.log.warning('检测：', log, ('未识别，识别度为 %.3f' % max_val), ('，要求达到 %.3f' % threshold), sep="")
        time.sleep(wait_time)
        return he.ERROR
    else:
        he.log.event('检测：', log, ('识别成功，识别度为 %.3f' % max_val), ' [检测点 ',
                     (click_point[0], click_point[1]), "]", sep="")
        time.sleep(wait_time)
        return he.OK


def click_multiple_possible_images(
    *template_src_list: str, width_offset_rate=0.5, height_offset_rate=0.5, threshold=0.6, log="", wait_time=0.0, zoom_in_and_out=True
) -> int:
    global last_best_rate
    if log != "": log = '"' + log + '" '
    origin_screenshot = he.pag.screenshot()
    screenshot = cv.cvtColor(np.array(origin_screenshot), cv.COLOR_RGB2BGR)
    most_similar_template_img, most_similar_click_point, most_similar_max_val = None, [0, 0], 0
    for template_src in template_src_list:
        template_src_path = _get_img_path(template_src)
        template_img = cv.imread(template_src_path)
        if zoom_in_and_out:
            if last_best_rate > 0 and threshold is not None:
                click_point, max_val = detect_zoom_with_rate(screenshot, template_img, last_best_rate)
                if max_val < threshold:
                    click_point, max_val, last_best_rate = detect_zoom_in_and_out(screenshot, template_img)
            else:
                click_point, max_val, last_best_rate = detect_zoom_in_and_out(screenshot, template_img)
        else:
            click_point, max_val = detect_no_zoom(screenshot, template_img)
        if max_val > most_similar_max_val:
            most_similar_template_img = template_img
            most_similar_click_point = click_point
            most_similar_max_val = max_val
    if threshold is not None and most_similar_max_val < threshold:
        he.log.warning('点击（多个可能图像）：', log, ('未识别，最高识别度为 %.3f' % most_similar_max_val), ('，要求达到 %.3f' % threshold), sep="")
        time.sleep(wait_time)
        return he.ERROR
    else:
        w_bias = int(most_similar_template_img.shape[1] * width_offset_rate)
        h_bias = int(most_similar_template_img.shape[0] * height_offset_rate)
        he.log.event('点击（多个可能图像）：', log, ('识别成功，最高识别度为 %.3f' % most_similar_max_val), ' [点击 ',
                     (most_similar_click_point[0] + w_bias, most_similar_click_point[1] + h_bias), "]", sep="")
        he.pag.click(most_similar_click_point[0] + w_bias, most_similar_click_point[1] + h_bias)
        time.sleep(wait_time)
        return he.OK


def compare(*template_src_list: str, log="", wait_time=0.0, zoom_in_and_out=True, zoom_use_previous_rate=True) -> int:
    global last_best_rate
    if log != "": log = '"' + log + '" '
    origin_screenshot = he.pag.screenshot()
    screenshot = cv.cvtColor(np.array(origin_screenshot), cv.COLOR_RGB2BGR)
    ans = []
    for template_src in template_src_list:
        template_src_path = _get_img_path(template_src)
        template_img = cv.imread(template_src_path)
        if zoom_in_and_out and last_best_rate > 0 and zoom_use_previous_rate:
            max_loc, max_val = detect_zoom_with_rate(screenshot, template_img, last_best_rate)
        elif zoom_in_and_out:
            # 不更新 last_rate，防止不一致
            max_loc, max_val, _ = detect_zoom_in_and_out(screenshot, template_img)
        else:
            max_loc, max_val = detect_no_zoom(screenshot, template_img)
        ans.append(max_val)
    he.log.event('图像对比：', log, "对比列表 ", ans, sep="")
    time.sleep(wait_time)
    return ans.index(max(ans))


def qrcode_detect(*, log="", wait_time=0.0) -> int:
    origin_screenshot = he.pag.screenshot()
    screenshot = cv.cvtColor(np.array(origin_screenshot), cv.COLOR_RGB2BGR)
    gray_screenshot = cv.cvtColor(np.array(origin_screenshot), cv.COLOR_RGB2GRAY)
    qrcode = cv.QRCodeDetector()
    result_detection, transform, straight_qrcode = qrcode.detectAndDecode(gray_screenshot)
    if transform is not None:
        he.log.event("二维码检测：检测到", log, "二维码，正在保存", sep="")
        cv.imwrite(_get_qrcode_path(str(time.time())), screenshot)
        time.sleep(wait_time)
        return he.OK
    else:
        he.log.warning("二维码检测：未检测到", log, "二维码", sep="")
        time.sleep(wait_time)
        return he.ERROR
