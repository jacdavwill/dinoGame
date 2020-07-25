from pynput.keyboard import Key, Controller
import random
from enum import IntEnum
import pyautogui
import time
import math
from prettytable import PrettyTable

# Navigate to chrome://dino and make the chrome window fill left half of screen.

# random
keyboard_input = Controller()
min_speed = 6
max_speed = 13
num_speeds = max_speed - min_speed + 1
current_speed = min_speed
acceleration = .065  # speed/sec
# todo: make all points based on two corners only
low = 440
mid = 397
startX = 70
endX = 449
width = endX - startX + 1
step = 10
jump_states = 3  # grounded, low, high
levels = 2  # 2 = low obstacle, 1 = high obstacle
game_over_corners = [(456, 377), (502, 417)]
learning_rate = 0.05
start_time = time.time()
num_states = levels * round(width / step) * (max_speed - min_speed + 1) * jump_states  # 2 * 38 * 8 * 3 = 1,824
iterations = 0
current_reward = 0

jumping_state = 0  # 0 = ground, 1 = low, 2 = high
jump_start_time = 0
jump_low_duration = 0.125
jump_duration = 0.5  # seconds from jump to land


def has_obstacle(pixel):
    return (170 < pixel[0] < 175) or pixel[0] < 10


def get_obstacle_dist(img):
    dist_mid = round(width / step)
    dist_low = round(width / step)

    for y in range(startX, endX):
        if has_obstacle(img.getpixel((y, mid))):
            dist_mid = math.floor((y - startX) / step)
            break
    for z in range(startX, endX):
        if has_obstacle(img.getpixel((z, low))):
            dist_low = math.floor((z - startX) / step)
            break

    return (dist_low, 2) if dist_low < dist_mid else (dist_mid, 1)


def load_q_table(num_states, num_actions, initial_val):
    table = []
    for state in range(num_states):
        value = []
        for action in range(num_actions):
            value.append(initial_val)
        table.append(value)
    return table


def is_game_over(img):
    for site in game_over_corners:
        if not has_obstacle(img.getpixel(site)):
            return False
    return True


def press(key):
    keyboard_input.press(key)
    keyboard_input.release(key)


def restart():
    global current_speed, start_time, iterations, current_reward, jumping_state
    time.sleep(1)
    press(Key.space)
    time.sleep(4)  # sleep while no obstacles are in sight
    current_speed = min_speed
    jumping_state = 0
    current_reward = 0
    iterations += 1
    start_time = time.time()


def get_jump_state(current_time):
    if jumping_state == 0:
        return 0  # jump state is ground
    time_since_jump = current_time - jump_start_time
    if time_since_jump >= jump_low_duration and (time_since_jump < (jump_duration - jump_low_duration)):
        return 2  # jump state is high
    else:
        return 1  # jump state is low


def encode_state(obst, speed, jumping):
    #      dist      obs level
    return obst[0] * obst[1] * num_speeds * jump_states + speed + jumping


def choose_action(action_space):
    if jumping_state != 0:  # if you are jumping, then do nothing
        return 0
    rand_pos = random.uniform(0, sum(action_space))
    for action, action_value in enumerate(action_space):
        if rand_pos < action_value:
            return action
        else:
            rand_pos -= action_value
    return 0


def bounded(val, min=0.1, max=9.9):
    if val < min:
        return min
    elif val > max:
        return max
    else:
        return val


def update_q_table(q_table, state, action, reward):
    curr_value = q_table[state][action]
    q_table[state][action] = ((1 - learning_rate) * curr_value) + (learning_rate * reward)


def take_action(action):
    global jumping_state
    global jump_start_time
    if action == Actions.JUMP:
        if jumping_state == 0:  # if dino is walking
            jumping_state = 1
            jump_start_time = time.time()
        press(Key.space)


def output_q_table(current_table, speed, level):
    print("Q_table for speed: ", speed, " obstacle level: ", level)
    table = PrettyTable(["Jump"] + list(range(0, width, step)))
    for jump_state in range(jump_states):
        vals = [current_table[encode_state((x, level), speed, jump_state)] for x in range(round(width / step))]
        formatted_vals = [[round(x, 2), round(y, 2)] for [x, y] in vals]
        table.add_row([jump_state] + formatted_vals)
    print(table)


class Actions(IntEnum):
    NOTHING = 0
    JUMP = 1


q_table = load_q_table(num_states, len(Actions), initial_val=5)
last_state = 0  # encode_state(get_obstacle_dist(img), current_speed)
last_action = Actions.NOTHING


while True:
    time_step = time.time()

    img = pyautogui.screenshot()
    if is_game_over(img):
        update_q_table(q_table, last_state, last_action, -10)
        print("Iteration: ", iterations, " reward: ", current_reward, " time: ", time_step - start_time)
        restart()
    else:
        reward = 5 if last_action == Actions.NOTHING else 2  # this incentivizes doing nothing unless it is required
        update_q_table(q_table, last_state, last_action, reward)
        current_reward += reward

    output_q_table(q_table, min_speed, 2)
    current_speed = round(min((time_step - start_time) * acceleration + min_speed, max_speed))
    last_state = encode_state(get_obstacle_dist(img), current_speed, get_jump_state(time_step))
    current_action_space = q_table[last_state]
    last_action = choose_action(current_action_space)
    take_action(last_action)

    # print(get_obstacle_dist(img))
    # print(pyautogui.position())
    # print(pyautogui.pixel(*pyautogui.position()))
    # time.sleep(.5)
