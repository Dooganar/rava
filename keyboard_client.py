#!/usr/bin/env python3
"""
keyboard_client.py
Sends 2-byte UDP packets when ← / → are pressed in the terminal.

Packet = bytes([0x01, action]) where action is:
  0x00 = LEFT,  0x01 = RIGHT
'q' to quit.

Use a terminal (not a GUI run button). Works well over Raspberry Pi Connect.
"""

import socket
import time
import curses

HOST = "127.0.0.1"   # point to the Pi running motor_server.py
PORT = 50555
USER_ID = 0x01

def send(sock, action_id):
    pkt = bytes([USER_ID, action_id])
    sock.sendto(pkt, (HOST, PORT))

def ui(stdscr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    stdscr.clear()
    stdscr.addstr(0, 0, "Keyboard → UDP sender")
    stdscr.addstr(2, 0, f"Target: {HOST}:{PORT}, USER_ID=0x{USER_ID:02X}")
    stdscr.addstr(4, 0, "← Left  : send {0x01, 0x00}")
    stdscr.addstr(5, 0, "→ Right : send {0x01, 0x01}")
    stdscr.addstr(7, 0, "q       : quit")
    stdscr.refresh()

    try:
        while True:
            k = stdscr.getch()
            if k == -1:
                time.sleep(0.01)
                continue
            if k in (ord('q'), ord('Q')):
                break
            if k == curses.KEY_LEFT:
                send(sock, 0x00)
                stdscr.addstr(9, 0, "Sent LEFT  {0x01, 0x00}   ")
                stdscr.refresh()
            elif k == curses.KEY_RIGHT:
                send(sock, 0x01)
                stdscr.addstr(9, 0, "Sent RIGHT {0x01, 0x01}   ")
                stdscr.refresh()
            else:
                # optional debug: show key codes
                stdscr.addstr(11, 0, f"(debug) key code: {k}     ")
                stdscr.refresh()
    finally:
        sock.close()

def main():
    curses.wrapper(ui)

if __name__ == "__main__":
    main()

