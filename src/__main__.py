#!/usr/bin/env python3
'''
xpybar – xmobar replacement written in python
Copyright © 2014  Mattias Andrée (maandree@member.fsf.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import Xlib.display, Xlib.Xatom, Xlib.ext.randr, Xlib.X

from x import *


open_x()

width, height, left, top, panel_height, at_top = get_monitors()[0][:3] + [24, 1 * 12, True]
print(width, height, left, top)

display = get_display()
window = create_panel(width, height, left, top, panel_height, at_top)
gc = window.create_gc()

window.map()
display.flush()

while True:
    try:
        e = display.next_event()
        if e.type == Xlib.X.DestroyNotify:
            break
    except KeyboardInterrupt:
        break
    gc.change(foreground = get_screen().black_pixel)
    window.fill_rectangle(gc, 0, 0, width, panel_height)
    display.flush()

window.unmap()
close_x()

