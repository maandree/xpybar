#!/usr/bin/env python3

import time

import Xlib.display

display = Xlib.display.Display()
screen = display.screen()

window = screen.root.create_window(0, 0, 100, 100, 0, screen.root_depth)

window.map()
display.flush()
time.sleep(1)
display.close()


