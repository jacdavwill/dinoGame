from pynput.keyboard import Key, Controller
from pynput import keyboard
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
jump_states = 4  # grounded, rise, peak, fall
levels = 2  # 2 = low obstacle, 1 = high obstacle
min_reward = 0.1
max_reward = 9.9
game_over_corners = [(456, 377), (502, 417)]
learning_rate = 0.05
future_devaluation = 0.25
start_time = time.time()
num_states = levels * round(width / step) * (max_speed - min_speed + 1) * jump_states  # 2 * 38 * 8 * 4 = 2,432
iterations = 0


class Actions(IntEnum):
    NOTHING = 0
    JUMP = 1


class JumpStates(IntEnum):
    GROUND = 0
    RISE = 1
    PEAK = 2
    FALL = 3


class State:
    def __init__(self, dist, level, jump_state, speed):
        self.dist = dist
        self.level = level
        self.jump_state = jump_state
        self.speed = speed

    def __hash__(self):
        return hash(self.dist) * hash(self.level) * hash(self.speed) * jump_states + self.jump_state

    def __eq__(self, other):
        return self.dist == other.dist and self.level == other.level and self.jump_state == other.jump_state and self.speed == other.speed


jumping_state = JumpStates.GROUND
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


def load_q_table(num_actions, initial_val):
    table = {}
    for dist in range(round(width / step)):
        for level in [1, 2]:
            for jump_state in range(jump_states):
                for speed in range(min_speed, max_speed + 1):
                    table[State(dist, level, jump_state, speed)] = [initial_val for i in range(num_actions)]
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
    jumping_state = JumpStates.GROUND
    current_reward = 0
    iterations += 1
    start_time = time.time()


def get_jump_state(current_time):
    if jumping_state == JumpStates.GROUND:
        return JumpStates.GROUND
    time_since_jump = current_time - jump_start_time
    if time_since_jump >= jump_low_duration and (time_since_jump < (jump_duration - jump_low_duration)):
        return 2  # jump state is high
    else:
        return 1  # jump state is low


def choose_action(action_space):
    if jumping_state != JumpStates.GROUND:
        return Actions.NOTHING
    rand_pos = random.uniform(0, sum(action_space))
    for action, action_value in enumerate(action_space):
        if rand_pos < action_value:
            return action
        else:
            rand_pos -= action_value
    return Actions.NOTHING


def bounded(val, min=min_reward, max=max_reward):  # can be removed if all rewards remain in min-max reward range
    if val < min:
        return min
    elif val > max:
        return max
    else:
        return val


def get_future_reward(table, state, action):
    future_state = None
    if state.dist == 0:
        if state.jump_state == JumpStates.PEAK:
            return max_reward
        else:
            return min_reward

    if action == action.NOTHING:
        future_state = State(state.dist - 1, state.level, state.jump_state, state.speed)
    else:
        next_jump_state = (state.jump_state + 1) % jump_states
        future_state = State(state.dist - 1, state.level, next_jump_state, state.speed)

    return max(table[future_state])


def update_q_table(q_table, state, action, reward):
    curr_value = q_table[state][action]
    new_calc_reward = (reward + get_future_reward(q_table, state, action)) / 2
    q_table[state][action] = bounded(((1 - learning_rate) * curr_value) + (learning_rate * new_calc_reward))


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
        q_entries = [current_table[State(x, level, jumping_state, speed)] for x in range(round(width / step))]
        formatted_vals = [[round(x, 2), round(y, 2)] for [x, y] in q_entries]
        table.add_row([jump_state] + formatted_vals)
    print(table)


q_table = load_q_table(len(Actions), initial_val=5)
last_state = current_state = State(0, 2, JumpStates.GROUND, min_speed)  # starting state placeholder
last_action = Actions.NOTHING


# def on_press(key):
#     img = pyautogui.screenshot()
#     print(get_obstacle_dist(img)[0])
#
#
# def on_release(key):
#     val = 2 + 4
#
#
# with keyboard.Listener(
#     on_press=on_press,
#     on_release=on_release
# ) as listener:
#     listener.join()

while True:
    time_step = time.time()

    img = pyautogui.screenshot()
    if is_game_over(img):
        update_q_table(q_table, last_state, last_action, min_reward)
        print("Iteration: ", iterations, " time: ", time_step - start_time)
        restart()
    else:
        if current_state != last_state:
            reward = max_reward if last_action == Actions.NOTHING else 2  # this incentivizes doing nothing unless it is required
            update_q_table(q_table, last_state, last_action, reward)

    output_q_table(q_table, min_speed, 2)
    current_speed = round(min((time_step - start_time) * acceleration + min_speed, max_speed))

    last_state = current_state
    current_state = State(*get_obstacle_dist(img), get_jump_state(time_step), current_speed)

    current_action_space = q_table[current_state]
    last_action = choose_action(current_action_space)
    take_action(last_action)



    # print(get_obstacle_dist(img))
    # print(pyautogui.position())
    # print(pyautogui.pixel(*pyautogui.position()))
    # time.sleep(.5)
