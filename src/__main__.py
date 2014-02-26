#!/usr/bin/env python3

import time, sys
import Xlib.display, Xlib.Xatom, Xlib.ext.randr, Xlib.X

WIDTH, HEIGHT, LEFT, TOP, Y = 1600, 12, 1600, 24, 1200 - 24 - 12

display = Xlib.display.Display()
screen = display.screen()

window = screen.root.create_window(LEFT, Y, WIDTH, HEIGHT, 0, screen.root_depth,
                                   Xlib.X.InputOutput, Xlib.X.CopyFromParent,
                                   event_mask = (
                                       Xlib.X.StructureNotifyMask |
                                       Xlib.X.ButtonReleaseMask
                                   ),
                                   colormap = Xlib.X.CopyFromParent)

window.set_wm_name('xpybar')
window.set_wm_icon_name('xpybar')
window.set_wm_class('bar', 'xpybar')

_CARD = display.intern_atom("CARDINAL")
_PSTRUT = display.intern_atom("_NET_WM_STRUT_PARTIAL")
window.change_property(_PSTRUT, _CARD, 32, topx(LEFT, TOP, WIDTH, HEIGHT))

top    = lambda x, y, width, height : [0, 0, y + height, 0, 0, 0, 0, 0, x, x + width, 0, 0]
bottom = lambda x, y, width, height : [0, 0, 0, y + height, 0, 0, 0, 0, 0, 0, x, x + width]

_ATOM = display.intern_atom("ATOM")
_TYPE = display.intern_atom("_NET_WM_WINDOW_TYPE")
_DOCK = display.intern_atom("_NET_WM_WINDOW_TYPE_DOCK")
window.change_property(_TYPE, _ATOM, 32, [_DOCK])

gc = window.create_gc()

window.map()
display.flush()

e = None
while True:
    try:
        e = display.next_event()
        if e.type == Xlib.X.DestroyNotify:
            break
    except KeyboardInterrupt:
        break
    gc.change(foreground = screen.black_pixel)
    window.fill_rectangle(gc, 0, 0, 1600, 12)
    display.flush()

window.unmap()
display.flush()
display.close()

