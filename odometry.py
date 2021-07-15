import RPi.GPIO as GPIO
import time
import math
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

state_last_left = GPIO.input(6)
rotation_count_left = 0
state_count_left = 0

state_last_right = GPIO.input(5)
rotation_count_right = 0
state_count_right = 0

tick_number = 20
distance_between_wheels = 13
wheel_radius = 3


def start_tracking_left():
    global state_count_left, state_last_left
    while 1:
        state_current_left = GPIO.input(6)

        if state_current_left != state_last_left:
            state_last_left = state_current_left
            state_count_left += 1
        time.sleep(0.1)


def start_tracking_right():
    global state_count_right, state_last_right
    while 1:
        state_current_right = GPIO.input(5)
        if state_current_right != state_last_right:
            state_last_right = state_current_right
            state_count_right += 1
        time.sleep(0.1)


def wheel_rotation_distance_in_cm(tick, r=wheel_radius, n=tick_number):
    distance = 2 * math.pi * r * tick / n
    return distance


def last_position():
    distance_left = wheel_rotation_distance_in_cm(state_count_left)
    distance_right = wheel_rotation_distance_in_cm(state_count_right)
    distance_center = (distance_left + distance_right) / 2
    phi_angle = (distance_left + distance_right) / distance_between_wheels
    x_prime = distance_center * math.cos(phi_angle)
    y_prime = distance_center * math.sin(phi_angle)
    return x_prime, y_prime


def position_text(x, y):
    if math.isclose(x, 0, abs_tol=2.5) and math.isclose(y, 0, abs_tol=2.5):
        return "merkez"

    if math.isclose(x, 0, abs_tol=2.5):
        if y > 2.5:
            return "ileri"
        elif y < 2.5:
            return "geri"

    if x > 2.5:
        if math.isclose(y, 0, abs_tol=2.5):
            return "sağ"
        elif y > 2.5:
            return "sağ-ileri"
        else:
            return "sağ-geri"

    if x < 2.5:
        if math.isclose(y, 0, abs_tol=2.5):
            return "sol"
        if y > 2.5:
            return "sol-ileri"
        if y < 2.5:
            return "sol-geri"


# start tracking thread
track_thread_left = threading.Thread(target=start_tracking_left)
track_thread_left.setDaemon(True)
track_thread_left.start()
track_thread_right = threading.Thread(target=start_tracking_right)
track_thread_right.setDaemon(True)
track_thread_right.start()
