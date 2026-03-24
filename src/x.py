#!/usr/bin/env python3
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016, 2017, 2018, 2019, 2026  Mattias Andrée (m@maandree.se)

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

import os, subprocess
import Xlib.display, Xlib.Xatom, Xlib.ext.randr, Xlib.X


display = None
'''
The connection the X display
'''

screen = None
'''
The screen the panel is placed in
'''

screen_i = None
'''
The index of the screen `screen`
'''


def open_x(screen_no = None):
    '''
    Open connection the X and select screen
    
    @param  screen_no:int?  The index of the screen to use, `None` for default
    '''
    global display, screen, screen_i
    display = Xlib.display.Display()
    screen_i = screen_no if screen_no is not None else display.get_default_screen()
    screen = display.screen(screen_i)


def get_monitors():
    '''
    Returns the pixel size and position of the monitors in the screen
    
    @return  :list<(width:int, height:int, left:int, top:int)>
             The width, height, left position and top position of each
             monitor, starting with the primary output
    '''
    global screen_i
    p = subprocess.Popen(['xrandr'], stdout = subprocess.PIPE)
    p = p.communicate()[0].decode('utf-8', 'replace')
    s = -1
    rc = []
    prim = None
    for line in p.split('\n'):
        if line.startswith('Screen '):
            s = int(line[len('Screen '):].split(':')[0])
        elif s == screen_i:
            if ' connected ' in line:
                try:
                    m = line.replace('-', '+-').replace('++', '+')
                    p = ' primary ' in m
                    m = m.replace(' primary ', ' ')
                    m = m.split(' ')[2].replace('+', 'x').split('x')
                    m = [int(x) for x in m]
                    if p and (prim is None):
                        prim = m
                    else:
                        rc.append(m)
                except:
                    pass # Output not used
    if prim is not None:
        rc = [prim] + rc
    return rc


def get_display():
    '''
    Returns the X display
    '''
    global display
    return display


def get_screen():
    '''
    Returns the X screen
    '''
    global screen
    return screen


def get_event_mask():
    '''
    For `create_panel`, return which events should be caught
    
    @return  :int  Mask of events that should be caught
    '''
    return (Xlib.X.StructureNotifyMask |
            Xlib.X.ButtonPressMask |
            Xlib.X.ButtonReleaseMask |
            Xlib.X.ExposureMask)


def get_override_redirect():
    '''
    For `create_panel`, figure out whether override_redirect should be set
    
    @return  :bool  Whether override_redirect should be set
    '''
    if 'DESKTOP_SESSION' in os.environ:
        desktop = os.environ['DESKTOP_SESSION']
        if desktop in ('xmonad',):
            return False
    return True


def create_panel(width, height, left, ypos, panel_height, at_top, top = 0, xpos = 0, panel_width = None, at_left = True, sidebar = False):
    '''
    Create a docked panel, not mapped yet
    
    @param   width:int         The width of the output
    @param   height:int        The height of the output
    @param   left:int          The left position of the output
    @param   ypos:int          The position of the panel in relation to either the top or bottom edge of the output
    @param   panel_height:int? The height of the panel, `None` for `height`
    @param   at_top:bool       Whether the panel is to be docked to the top of the output, otherwise to the bottom
    @param   top:int           The top position of the output
    @param   xpos:int          The position of the panel in relation to either the left or right edge of the output
    @param   panel_width:int?  The width of the panel, `None` for `width`
    @param   at_left:bool      Whether the panel is to be docked to the left edge of the output, otherwise to the right edge
    @param   sidebar:bool      If `True`, the panel will be docked to the left or right edge,
                               otherwise it will be docked to the top or the bottom edge
    @return                    The window
    '''
    global display, screen

    sw, sh = screen['width_in_pixels'], screen['height_in_pixels']

    if sidebar:
        if panel_height is None:
            panel_height = height
    else:
        if panel_width is None:
            panel_width = width

    w, h = panel_width, panel_height
    y = top + (ypos if at_top else (height - ypos - h))
    x = left + (xpos if at_left else (width - xpos - w))
    window = screen.root.create_window(x, y, panel_width, panel_height, 0,
                                       Xlib.X.CopyFromParent,
                                       Xlib.X.InputOutput,
                                       Xlib.X.CopyFromParent,
                                       event_mask = get_event_mask(),
                                       colormap = Xlib.X.CopyFromParent,
                                       override_redirect = get_override_redirect())

    window.set_wm_name('xpybar')
    window.set_wm_icon_name('xpybar')
    window.set_wm_class('bar', 'xpybar')
    window.set_wm_client_machine(os.uname().nodename)

    if sidebar:
        if at_left:
            position = [x + w, 0, 0, 0,     y, y + h - 1, 0, 0,    0, 0, 0, 0]
        else:
            position = [0, sw - x, 0, 0,    0, 0, y, y + h - 1,    0, 0, 0, 0]
    else:
        if at_top:
            position = [0, 0, y + h, 0,    0, 0, 0, 0,    x, x + w - 1, 0, 0]
        else:
            position = [0, 0, 0, sh - y,   0, 0, 0, 0,    0, 0, x, x + w - 1]
    _CARD    = display.intern_atom("CARDINAL")
    _PSTRUT  = display.intern_atom("_NET_WM_STRUT_PARTIAL")
    _STRUT   = display.intern_atom("_NET_WM_STRUT")
    _DESKTOP = display.intern_atom("_NET_WM_DESKTOP")
    _PID     = display.intern_atom("_NET_WM_PID")
    window.change_property(_PSTRUT,  _CARD, 32, position)
    window.change_property(_STRUT,   _CARD, 32, position[:4])
    window.change_property(_DESKTOP, _CARD, 32, [0xFFFFFFFF])
    window.change_property(_PID,     _CARD, 32, [os.getpid()])
    
    _ATOM = display.intern_atom("ATOM")
    _TYPE = display.intern_atom("_NET_WM_WINDOW_TYPE")
    _DOCK = display.intern_atom("_NET_WM_WINDOW_TYPE_DOCK")
    window.change_property(_TYPE, _ATOM, 32, [_DOCK])
    
    return window


def draw_text(window, gc, x, y, text):
    '''
    Draw a text on a window
    
    @param  window    The window
    @param  gc        The window's graphics context
    @param  x:int     The left position of the text
    @param  y:int     The Y position of the bottom of the text
    @param  text:str  The text to draw
    '''
    text_ = text.encode('utf-16')[2:]
    text = []
    for i in range(len(text_)):
        if (i & 1) == 0:
            text.append(text_[i])
        else:
            text[-1] |= text_[i] << 8
    window.image_text_16(gc, x, y, text)


def close_x():
    '''
    Closes the connection to X, but flushes it first
    '''
    global display
    display.flush()
    display.close()
