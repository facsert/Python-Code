"""
Author: facsert
Date: 2023-08-07 21:42:54
LastEditTime: 2023-08-07 22:11:14
LastEditors: facsert
Description: 
"""

from time import sleep


def progress_bar(progress, length=50):
    block = int(round(length * progress))
    text = f"[{'#' * block + '-' * (length - block)}] {progress * 100:.2f}%"
    print(text, end="\r")


def wait(delay=1, length=50):
    use = 0
    while use < delay:
        block = int(round(length * use / delay))
        text = f"[{'#' * block + '-' * (length - block)}]"
        print(f"Please wait {delay}s {text} {use}s", end="\r")
        sleep(1)
        use += 1

    print(f"Please wait {delay}s [{'#' * (length)}] {use}s")


if __name__ == "__main__":
    wait(10)
