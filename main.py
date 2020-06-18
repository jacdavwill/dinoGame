from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyautogui
from random import uniform
from time import time, sleep as sleeper

# Navigate to chrome://dino and make the chrome window fill left half of screen.

# random
keyboard_input = Controller()
min_speed = 6
max_speed = 13
acceleration = .065  # speed/sec
low = 430
mid = 400
startX = 100
endX = 500
stepX = 100
levels = 2
ref = (500, 700)
sites = []
for i in range(startX, endX, stepX):
    sites.append((i, low))
    sites.append((i, mid))


def get_key_name(key):
    if isinstance(key, keyboard.KeyCode):
        return key.char
    else:
        return str(key)


def (x, y, back_is_black):
    color = pyautogui.pixel(x, y)
    if (color[0] < 100 and back_is_black) or (color[0] > 100 and not back_is_black):
        return 3
    else:
        return 10


def sleep(x):
    sleeper(uniform(x, x))


def encode(site_spots, speed):
    index = 0
    for j in range(len(sites)):
        if site_spots[j]:
            index += pow(2, j)
    return index * (speed - min_speed + 1)


actions = 3  # jump, duck, do nothing
states = pow(2, levels * len(sites)) * (max_speed - min_speed)  # 1792=2^8*7
print(encode([True,True,True,True,True,True,True,True], 7))


# start_time = time()
# while True:
#     start = time()
#     background = pyautogui.pixel(ref[0], ref[1])[0] < 100
#     site_vals = [get_color_val(site[0], site[1], background) for site in sites]
#     site_vals.append(int(time() - start_time))
#     print("delta: ", time() - start)
#     sleep(1)
