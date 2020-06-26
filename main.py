from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyautogui
import time

# Navigate to chrome://dino and make the chrome window fill left half of screen.

# random
keyboard_input = Controller()
min_speed = 6
max_speed = 13
acceleration = .065  # speed/sec
# todo: make all points based on two corners only
low = 440
mid = 397
startX = 70
endX = 450
width = endX - startX
height = low - mid
levels = 2
ref = (500, 700)


def is_dark(pixel):
    return pixel[0] < 100


def has_obstacle(pixel, back_is_dark):
    return is_dark(pixel) != back_is_dark


def get_obstacle_dist(img):



def load_q_table(num_states, all_actions, initial_val):
    table = []
    for state in range(num_states):
        value = {}
        for action in all_actions:
            value[action] = initial_val
        table.append(value)
    return table


NOTHING = 0
DUCK = 1
JUMP = 2
actions = [NOTHING, DUCK, JUMP]
states = levels *  1 # pow(2, levels * len(sites)) * (max_speed - min_speed + 1)  # 2040=2^8*8
q_table = load_q_table(states, actions, 1.0)

img = pyautogui.screenshot(region=(startX, mid, width, height))

# print(sites[6])
# start_time = time()
while True:
    # start = time.time()
    #     print("fps: ", 1.0 / float(time() - start))
    #     time.sleep(1)
    img = pyautogui.screenshot()
    img.crop()
    print(get_obstacle_dist(img))
    # print(pyautogui.position())
    # time.sleep(.5)
