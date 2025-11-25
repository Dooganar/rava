
from gpiozero import OutputDevice, PWMOutputDevice
from time import sleep

# Pin Definitions
IN1 = OutputDevice(12)
IN2 = OutputDevice(16)
IN3 = OutputDevice(20)
IN4 = OutputDevice(21)
# ENA = PWMOutputDevice(17)  # ENA for Motor 1
# ENB = PWMOutputDevice(27)  # ENB for Motor 2

# Define step sequence for the motor
step_sequence = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
]

def set_step(w1, w2, w3, w4):
    IN1.value = w1
    IN2.value = w2
    IN3.value = w3
    IN4.value = w4

def step_motor(steps, direction=1, delay=0.01):
    #ENA.value = 1  # Enable Motor 1
    #ENB.value = 1  # Enable Motor 2
    for _ in range(steps):
        for step in (step_sequence if direction > 0 else reversed(step_sequence)):
            set_step(*step)
            sleep(delay)
    #ENA.value = 0  # Disable Motor 1
    #ENB.value = 0  # Disable Motor 2

step_list = [25, 50, 10, 15]
direction_list = [1, -1, 1, 1]

ind = 0
max_index = len(step_list)

while True:
    step_motor(step_list[ind], direction_list[ind])
    if ind >= max_index:
        ind = 0
    sleep(4)
    ind += 1

