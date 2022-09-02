import time
import threading


def loop(objects):
    while True:
        time.sleep(1E6)


def reserve_browser_driver(browser):
    threading.Thread(target=loop, args=(browser,), daemon=True).start()


def series_func(func_list: list) -> None:
    if len(func_list) == 0:
        return
    for i in func_list:
        i.start()
        i.join()
    return


class LockThreads:
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
