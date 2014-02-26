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


OUTPUT, HEIGHT, YPOS, TOP = 0, 12, 24, True
FONT = '-misc-fixed-*-*-*-*-10-*-*-*-*-*-*-*'
BACKGROUND, FOREGROUND = (0, 0, 0), (192, 192, 192)


open_x()

width, height, left, top, panel_height, at_top = get_monitors()[OUTPUT][:3] + [YPOS, HEIGHT, TOP]

display = get_display()
window = create_panel(width, height, left, top, panel_height, at_top)
gc = window.create_gc()
cmap = window.get_attributes().colormap

window.map()
display.flush()

background = cmap.alloc_color(*[x * 257 for x in BACKGROUND]).pixel
foreground = cmap.alloc_color(*[x * 257 for x in FOREGROUND]).pixel
font = display.open_font(FONT)
font_q = font.query()
font_height = font_q.font_ascent + font_q.font_descent
text_width = lambda text : font.query_text_extents(text).overall_width

while True:
    try:
        e = display.next_event()
        if e.type == Xlib.X.DestroyNotify:
            break
    except KeyboardInterrupt:
        break
    gc.change(foreground = background)
    window.fill_rectangle(gc, 0, 0, width, panel_height)
    gc.change(foreground = foreground)
    gc.change(font = font)
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

