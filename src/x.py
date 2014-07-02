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

import subprocess
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
                m = line.replace('-', '+-').replace('++', '+')
                p = ' primary ' in m
                m = m.replace(' primary ', ' ')
                m = m.split(' ')[2].replace('+', 'x').split('x')
                m = [int(x) for x in m]
                if p and (prim is None):
                    prim = m
                else:
                    rc.append(m)
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


def create_panel(width, height, left, ypos, panel_height, at_top):
    '''
    Create a docked panel, not mapped yet
    
    @param   width:int         The width of the output
    @param   height:int        The height of the output
    @param   left:int          The left position of the output
    @param   ypos:int          The position of the panel in relation to either the top or bottom edge of the output
    @param   panel_height:int  The height of the panel
    @param   at_top:bool       Whether the panel is to be docked to the top of the output, otherwise to the bottom
    @return                    The window
    '''
    global display, screen
    ypos = ypos if at_top else (height - ypos - panel_height)
    window = screen.root.create_window(left, ypos, width, panel_height, 0,
                                       Xlib.X.CopyFromParent,
                                       Xlib.X.InputOutput,
                                       Xlib.X.CopyFromParent,
                                       event_mask = (
                                           Xlib.X.StructureNotifyMask |
                                           Xlib.X.ButtonReleaseMask |
                                           Xlib.X.ExposureMask
                                       ),
                                       colormap = Xlib.X.CopyFromParent)
    
    top_    = lambda x, y, w, h : [0, 0, y + h, 0, 0, 0, 0, 0, x, x + w, 0, 0]
    bottom_ = lambda x, y, w, h : [0, 0, 0, y + h, 0, 0, 0, 0, 0, 0, x, x + w]
    
    window.set_wm_name('xpybar')
    window.set_wm_icon_name('xpybar')
    window.set_wm_class('bar', 'xpybar')
    
    _CARD = display.intern_atom("CARDINAL")
    _PSTRUT = display.intern_atom("_NET_WM_STRUT_PARTIAL")
    window.change_property(_PSTRUT, _CARD, 32, (top_ if at_top else bottom_)(left, ypos, width, panel_height))
    
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

