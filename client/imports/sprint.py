
def warning(*words: any, sep=" ", end="\n"):
    print("\033[1;33mWARN ", end="")
    print(*words, sep=sep, end=end)
    print("\033[0m", end="")


def error(*words: any, sep=" ", end="\n"):
    print("\033[1;31mERROR ", end="")
    print(*words, sep=sep, end=end)
    print("\033[0m", end="")


def event(*words: any, sep=" ", end="\n"):
    print("\033[1;36mEVENT ", end="")
    print(*words, sep=sep, end=end)
    print("\033[0m", end="")


def tip(*words: any, sep=" ", end="\n"):
    print("TIP ", end="")
    print(*words, sep=sep, end=end)


def enter():
    print()
