import re
import ast
import json
import time
import argparse
from lockThreads import lock_threads
from goToClass import GoToClass, print_warning


class HelpMyClassPlease:
    def __init__(self) -> None:
        self.gtc = None
        self.args = None
        self.path = {}
        self.config = []
        self.today_list = []
        self.sleep_time = 60

    def parser(self):
        parser = argparse.ArgumentParser("help my class please")
        parser.add_argument('-t', '--test', nargs='?', type=str, const='[10, 1, 499]', default='[None]',
                            help="use a test time to run, you can change it by adding list of 3 int: [seconds pre "
                                 "minute, now weekday, now time]")
        parser.add_argument('-j', '--json', type=str, default="./class.json",
                            help="add your class.json path")
        self.args = parser.parse_args()
        self.args.test = ast.literal_eval(self.args.test)

    def init(self) -> None:
        self.read_config()
        self.gtc = GoToClass(self.path)
        self.today_list = [i for i in range(len(self.config))]
        print("\033[1;35mWarning: 如果开启 proxy，网页功能可能无法正常启动，请检查后再开启本程序\033[0m")
        print()

    def read_config(self) -> None:
        config = json.load(open(self.args.json, 'r', encoding='utf-8'))
        self.path = config[0]
        self.config = config[1]
        if len(self.config) > 0:
            print("\033[1;32m课程已从", self.args.json, "中导入\033[0m")

    def run(self) -> None:
        old_day = 0
        lck_threads = lock_threads()
        if self.args.test[0] is not None:
            sleep_time, weekday_for_test, time_for_test = self.args.test[0], self.args.test[1], self.args.test[2]
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
            if self.args.test[0] is not None:
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
                lck_threads.create(target=self.gtc.go_to_class, args=(self.config[i],), daemon=True)
            lck_threads.start_all()
            time.sleep(self.sleep_time)
            print()


if __name__ == "__main__":
    hmcp = HelpMyClassPlease()
    hmcp.parser()
    hmcp.init()
    hmcp.run()
