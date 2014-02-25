#!/usr/bin/env python3

import time
import Xlib.display, Xlib.Xatom

display = Xlib.display.Display()
screen = display.screen()

window = screen.root.create_window(0, 0, 100, 100, 0, screen.root_depth)

window.set_wm_name('xpybar')
window.set_wm_icon_name('xpybar')
window.set_wm_class('bar', 'xpybar')

_CARD = display.intern_atom("CARDINAL")
_PSTRUT = display.intern_atom("_NET_WM_STRUT_PARTIAL")
window.change_property(_PSTRUT, _CARD, 32, [0, 60, 0, 0, 0, 0, 24, 767, 0, 0, 0, 0])

_ATOM = display.intern_atom("ATOM")
_TYPE = display.intern_atom("_NET_WM_WINDOW_TYPE")
_DOCK = display.intern_atom("_NET_WM_WINDOW_TYPE_DOCK")
window.change_property(_TYPE, _ATOM, 32, [_DOCK])


window.map()
display.flush()

time.sleep(1)

window.unmap()
display.flush()
display.close()


