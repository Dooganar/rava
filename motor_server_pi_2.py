#!/usr/bin/env python3
"""
motor_server.py
Listens for 2-byte control packets over UDP and drives a stepper via RpiMotorLib.

Packet format (exactly 2 bytes):
  [ user_id, action_id ]
  user_id  : 0x01 (as requested; others ignored by default)
  action_id: 0x00 = LEFT  (counter-clockwise)
             0x01 = RIGHT (clockwise)

Emergency stop push-button on GPIO17 (RISING to 3V3).
"""

import socket
import time
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib

# ---------------- Configuration ----------------
HOST = "127.0.0.1"     # bind locally; change to Pi's IP if listening remotely
PORT = 50555           # UDP port
EXPECTED_USER = 0x01   # only act on this user ID (change/extend as needed)

# Motor pins (BCM) to L298 IN1..IN4
MOTOR_PINS = [12, 16, 20, 21]

# Motion parameters
STEP_DELAY = 0.005       # seconds between steps
STEPS_PER_BURST = 10    # steps per command
STEP_TYPE = "wave"       # "wave" | "full" | "half" | etc.
VERBOSE = True
INIT_DELAY = 0.0

# Emergency stop push-button
STOP_PIN = 17  # BCM
# ------------------------------------------------

# --- Always reset GPIO state at startup ---

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(STOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

motor = RpiMotorLib.BYJMotor("MyMotorOne", "Nema")

def button_callback(channel):
    print("[STOP] Button pressed → stopping motor immediately")
    try:
        motor.motor_stop()
    except Exception as e:
        print(f"[STOP] motor_stop error: {e}")

#GPIO.add_event_detect(STOP_PIN, GPIO.RISING, callback=button_callback, bouncetime=50)

def rotate(action_id: int):
    """Perform one burst in the direction encoded by action_id."""
    if action_id == 0x00:          # LEFT → CCW
        ccw = True
        label = "LEFT (CCW)"
    elif action_id == 0x01:        # RIGHT → CW
        ccw = False
        label = "RIGHT (CW)"
    else:
        print(f"[WARN] Unknown action_id {action_id:#04x}; ignoring")
        return

    print(f"[MOTOR] {label}: {STEPS_PER_BURST} steps, step_delay={STEP_DELAY}s, type={STEP_TYPE}")
    motor.motor_run(
        MOTOR_PINS,
        STEP_DELAY,
        STEPS_PER_BURST,
        ccw,
        VERBOSE,
        STEP_TYPE,
        INIT_DELAY,
    )

def main():
    print(f"[SERVER] UDP listening on {HOST}:{PORT}")
    print("[SERVER] Action map: 0x00=LEFT(CCW), 0x01=RIGHT(CW)")
    print("[SERVER] Press the physical STOP button to halt mid-run.")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(1.0)  # so we can exit cleanly with Ctrl+C

    try:
        while True:
            try:
                data, addr = sock.recvfrom(64)
            except socket.timeout:
                continue

            if len(data) != 2:
                print(f"[WARN] Ignoring packet with wrong length {len(data)} from {addr}")
                continue

            user_id, action_id = data[0], data[1]
            if user_id != EXPECTED_USER:
                print(f"[INFO] Packet for user {user_id:#04x} ignored (expected {EXPECTED_USER:#04x})")
                continue

            print(f"[RX] From {addr}: user={user_id:#04x}, action={action_id:#04x}")
            rotate(action_id)

    except KeyboardInterrupt:
        print("\n[SERVER] Ctrl+C → exiting")

    finally:
        try:
            motor.motor_stop()
        except Exception:
            pass
        GPIO.cleanup()
        sock.close()
        print("[SERVER] Cleaned up. Bye.")

if __name__ == "__main__":
    main()

