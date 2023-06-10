import re
import ast
import json
import time
import argparse

from hmcp_lib import log
from goToClass import GoToClass
from hmcp_lib.thread import LockThreads


class HelpMyClassPlease:
    def __init__(self) -> None:
        self.gtc = None
        self.args = None
        self.path = {}
        self.config = []
        self.today_list = []

    def parser(self):
        parser = argparse.ArgumentParser("help my class please")
        parser.add_argument(
            '-t', '--test', nargs='?', type=str, const='[10, 1, 499]', default='[None]',
            help="use a test time to run, you can change it by adding list of 3 int: [seconds pre "
            "minute, now weekday, now time]"
        )
        parser.add_argument(
            '-j', '--json', type=str, default="../config/class.json", help="add your class.json path"
        )
        self.args = parser.parse_args()
        self.args.test = ast.literal_eval(self.args.test)

    def init(self) -> None:
        self.read_config()
        self.gtc = GoToClass(self.path)
        self.today_list = [i for i in range(len(self.config))]
        log.warning("如果开启 proxy，网页功能可能无法正常启动，请检查后再开启本程序")
        log.enter()

    def read_config(self) -> None:
        config = json.load(open(self.args.json, 'r', encoding='utf-8'))
        self.path = config.get("path")
        self.config = config.get("class")
        log.info("课程已从", self.args.json, "中导入")
        if self.path is None or self.config is None:
            log.error("课程信息有误")

    def run(self) -> None:

        old_day = -1
        lck_threads = LockThreads()

        if self.args.test[0] is not None:
            sleep_time, weekday_for_test, time_for_test = self.args.test[0], self.args.test[1], self.args.test[2]
            log.warning(
                "当前为测试用例，时间流速与平常会有差异。测试参数 (每秒时长, 当前星期, 当前经过的分钟数) =",
                (sleep_time, weekday_for_test, time_for_test)
            )
            log.enter()

        while True:
            local_time = time.localtime(time.time())
            now_weekday = local_time.tm_wday + 1
            loop_sleep_time = 60 - local_time.tm_sec
            now_time = local_time.tm_hour * 60 + local_time.tm_min

            # test change
            if self.args.test[0] is not None:
                loop_sleep_time, now_weekday, now_time, time_for_test \
                    = sleep_time, weekday_for_test, time_for_test, time_for_test + 1

            if now_weekday - 1 != old_day:
                old_day = now_weekday - 1
                self.today_list = []
                log.info("新的一天开始啦～")
                for i in range(len(self.config)):
                    if now_weekday in self.config[i].setdefault("weekday", [0]):
                        self.today_list.append(i)
                if len(self.today_list) == 0:
                    log.info("今天没课啦！")
                else:
                    log.info("今天的课程有：")
                    for i in self.today_list:
                        log.info(
                            "课程名称：", self.config[i].setdefault("name", "<名称未知>"),
                            "　上课周：", self.config[i].get("weekday"),
                            "　上课时间：", self.config[i].setdefault("time", "0:0"),
                            "　课程时长：", self.config[i].setdefault("time_lasting", 100),
                            "min　进入时间范围：", self.config[i].setdefault("time_range", [-10, 15]), sep=""
                        )

            log.enter()
            log.just_color("heart-beat", color=log.blue_console)
            log.just_color(
                "当前时间：", "{:0>2d}:{:0>2d}:{:0>2d}".format(local_time.tm_hour, local_time.tm_min, local_time.tm_sec),
                "，星期", "零一二三四五六日"[now_weekday], sep=""
            )
            run_id_list = []
            for i in self.today_list.copy():
                start_time = re.split("[:：.]", self.config[i].get("time"))
                time_range = self.config[i].get("time_range")
                pre_time = int(start_time[0]) * 60 + int(start_time[1])
                if time_range[0] <= (now_time - pre_time) <= time_range[1]:
                    print(
                        "[课程选定] 名称: ", self.config[i].get("name"),
                        ", 时间: ", pre_time // 60, ":", ("%02d" % (pre_time % 60)), sep=""
                    )
                    run_id_list.append(i)
                    self.today_list.remove(i)
            for i in run_id_list:
                lck_threads.create(target=self.gtc.go_to_class, args=(self.config[i],), daemon=True)
            lck_threads.start_all()

            time.sleep(loop_sleep_time)


if __name__ == "__main__":
    hmcp = HelpMyClassPlease()
    hmcp.parser()
    hmcp.init()
    hmcp.run()
