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
    cmap = window.get_attributes().colormap
    gc.change(foreground = cmap.alloc_color(0x0000, 0x0000, 0x0000).pixel)
    window.fill_rectangle(gc, 0, 0, width, panel_height)
    gc.change(foreground = cmap.alloc_color(0xC0C0, 0xC0C0, 0xC0C0).pixel)
    gc.change(font = display.open_font('-misc-fixed-*-*-*-*-10-*-*-*-*-*-*-*'))
    text_ = '°°° TEST °°° ꚺ░∈𝕐 '.encode('utf-16')[2:]
    text = []
    for i in range(len(text_)):
        if (i & 1) == 0:
            text.append(text_[i])
        else:
            text[-1] |= text_[i] << 8
    window.image_text_16(gc, 0, 10, text)
    display.flush()

window.unmap()
close_x()

