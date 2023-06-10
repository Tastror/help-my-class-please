import logging
import logging.handlers

black_console = "30"
red_console = "31"
green_console = "32"
yellow_console = "33"
blue_console = "34"
purple_console = "35"
cyan_console = "36"
white_console = "37"


log_log = None
log_path = '../hmcp.log'


def _init():
    global log_log
    log_log = logging.getLogger("hmcp")
    log_log.setLevel(logging.DEBUG)
    hfh = logging.handlers.RotatingFileHandler(
        log_path, mode="a", maxBytes=1024 * 1024, backupCount=2
    )
    rh_formatter = logging.Formatter(
        "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
    )
    hfh.setFormatter(rh_formatter)
    log_log.addHandler(hfh)


def _change_print_to_log_msg(*args, **kwargs):
    res = ""
    sep = kwargs.get("sep", "")
    first = True
    for mem in args:
        if not first:
            res += sep
        res += str(mem)
        first = False
    return res


def _set_color(color):
    print("\033[1;" + color + "m", end="")


def _reset_color():
    print("\033[0m", end="")


def warning(*args, **kwargs):

    _set_color(yellow_console)
    print("WARN ", end="")
    print(*args, **kwargs)
    _reset_color()

    if log_log is None: _init()
    log_log.warning(_change_print_to_log_msg(*args, **kwargs))


def error(*args, **kwargs):

    _set_color(red_console)
    print("ERROR ", end="")
    print(*args, **kwargs)
    _reset_color()

    if log_log is None: _init()
    log_log.error(_change_print_to_log_msg(*args, **kwargs))


def event(*args, **kwargs):

    _set_color(cyan_console)
    print("EVENT ", end="")
    print(*args, **kwargs)
    _reset_color()

    if log_log is None: _init()
    log_log.info("EVENT " + _change_print_to_log_msg(*args, **kwargs))


def info(*args, **kwargs):

    _set_color(green_console)
    print("INFO ", end="")
    print(*args, **kwargs)
    _reset_color()

    if log_log is None: _init()
    log_log.info(_change_print_to_log_msg(*args, **kwargs))


def tip(*args, **kwargs):

    print("TIP ", end="")
    print(*args, **kwargs)

    if log_log is None: _init()
    log_log.info("TIP " + _change_print_to_log_msg(*args, **kwargs))


def just_color(*args, **kwargs):

    _set_color(kwargs.setdefault("color", white_console))
    kwargs.pop("color")
    print(*args, **kwargs)
    _reset_color()

    if log_log is None: _init()
    log_log.info(_change_print_to_log_msg(*args, **kwargs))


def enter():
    print()
    if log_log is None: _init()
    log_log.info("")
