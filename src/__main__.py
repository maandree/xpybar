#!/usr/bin/env python3
copyright = '''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016  Mattias Andrée (maandree@member.fsf.org)

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
import os, sys, pwd

import Xlib.threaded # IMPORTANT (threading do not work otherwise, see XInitThreads)
import Xlib.display, Xlib.Xatom, Xlib.ext.randr, Xlib.X
from argparser import *

from x import *
from util import *


PROGRAM_NAME = 'xpybar'
PROGRAM_VERSION = '1.17'


global OUTPUT, HEIGHT, YPOS, TOP, FONT, BACKGROUND, FOREGROUND
global display, outputs, redraw, Bar, start, stop
global conf_opts, config_file, parser

OUTPUT, HEIGHT, YPOS, TOP = 0, 12, 0, True
FONT = '-misc-fixed-*-*-*-*-10-*-*-*-*-*-*-*'
BACKGROUND, FOREGROUND = (0, 0, 0), (192, 192, 192)


PLUGIN_PATH = None
if PLUGIN_PATH is not None:
    sys.path.insert(0, PLUGIN_PATH)


def redraw():
    '''
    Invoked when redraw is needed,
    feel free to replace this completely
    '''
    global bar
    bar.clear()

def start():
    '''
    Invoked when it is time to create panels and map them,
    feel free to replace this completely
    '''
    global bar
    bar = Bar(OUTPUT, HEIGHT, YPOS, TOP, FONT, BACKGROUND, FOREGROUND)
    bar.map()

def stop():
    '''
    Invoked when it is time to unmap the panels,
    feel free to replace this completely
    '''
    global bar
    bar.unmap()

def unhandled_event(e):
    '''
    Invoked when an unrecognised even is polled,
    feel free to replace this completely
    
    @param  e  The event
    '''
    pass


class Bar:
    '''
    Docked panel
    
    @variable  window            The X window
    @variable  gc                The window's graphics context
    @variable  cmap              The window's colour map
    
    @variable  width:int         The output's pixel width
    @variable  height:int        The output's pixel height
    @variable  left:int          The output's left position
    @variable  ypos:int          The position of the panel in relation to either the top or bottom edge of the output
    @variable  panel_height:int  The panel's height
    @variable  at_top:bool       Whether the panel is to be docked to the top of the output, otherwise to the bottom
    
    @variable  background        The default background
    @variable  foreground        The default foreground
    @variable  font              The default font
    @variable  font_metrics      The default font's metrics
    @variable  font_height:int   The height of the default font
    @variable  font_width:int    The width of an 'X' with the default font
    @variable  palette           A 16-array of standard colours
    @variable  cmap_cache        Custom colour map cache
    '''
    
    def __init__(self, output, height, ypos, top, font, background, foreground):
        '''
        Constructor
        
        @param  output:int                                 The index of the output within the screen as printed by xrandr, except primary is first
        @param  height:int                                 The height of the panel
        @param  ypos:int                                   The position of the panel in relation the either the top or bottom edge of the output
        @param  top:bool                                   Whether the panel is to be docked to the top of the output, otherwise to the bottom
        @param  font:str                                   The default font
        @param  background:(red:int, green:int, blue:int)  The default background
        @param  foreground:(red:int, green:int, blue:int)  The default foreground
        '''
        ## Panel position
        pos = outputs[output][:3] + [ypos, height, top]
        self.width, self.height, self.left, self.ypos, self.panel_height, self.at_top = pos
        ## Create window and create/fetch resources
        self.window = create_panel(*pos)
        self.gc = self.window.create_gc()
        self.cmap = self.window.get_attributes().colormap
        ## Graphics variables
        self.cmap_cache = {}
        self.background = self.create_colour(*background)
        self.foreground = self.create_colour(*foreground)
        (self.font, self.font_metrics, self.font_height) = self.create_font(font)
        self.font_width = self.text_width('X')
        self.palette = [0x000000, 0xCD656C, 0x32A679, 0xCCAD47, 0x2495BE, 0xA46EB0, 0x00A09F, 0xD8D8D8]
        self.palette += [0x555555, 0xEB5E6A, 0x0EC287, 0xF2CA38, 0x00ACE0, 0xC473D1, 0x00C3C7, 0xEEEEEE]
        self.palette = [((p >> 16) & 255, (p >> 8) & 255, p & 255) for p in self.palette]
        self.palette = [self.create_colour(*p) for p in self.palette]
    
    def map(self):
        '''
        Map the window
        '''
        self.window.map()
        display.flush()
    
    def unmap(self):
        '''
        Unmap the window
        '''
        self.window.unmap()
    
    def text_width(self, text):
        '''
        Get the width of a text
        
        @param   text:str  The text
        @return  :int      The width of the text
        '''
        return self.font.query_text_extents(text.encode('utf8')).overall_width
    
    def draw_text(self, x, y, descent, text, *, colour = None, clear = None):
        '''
        Draw a text
        
        @param  x:int                             The left position of the text
        @param  y:int                             The Y position of the bottom of the text
        @param  descent:int                       Extra height under the text on each line
        @param  text:str                          The text to draw
        @param  colour:(foreground, background)?  The colour to draw with
        @param  clear:(y:int, height:int)?        Vertical clearing area
        '''
        special = '─│┌┐└┘├┤┬┴┼╱╲╳←↓→↑\0'
        buf = ''
        w = self.font_width - 1
        h = self.font_height + descent - 1
        y_ = y - self.font_height
        if colour is not None:
            (fc, bc) = colour
            self.gc.change(foreground = fc, background = bc)
        if clear is not None:
            (clear_y, line_height) = clear
            ascent = line_height - self.font_height
        for c in text + '\0':
            if c in special:
                if not buf == '':
                    text_width = self.font_width * len(buf)
                    if clear is not None:
                        self.change_colour(self.background)
                        self.window.fill_rectangle(self.gc, x, clear_y, text_width, ascent)
                        self.gc.change(foreground = fc, background = bc)
                    if len(buf.encode('utf-8')) > 255:
                        while not buf == '':
                            sbuf, buf = buf[:42], buf[42:]
                            draw_text(self.window, self.gc, x, y, sbuf)
                            x += self.font_width * len(sbuf)
                    else:
                        draw_text(self.window, self.gc, x, y, buf)
                        x += text_width
                        buf = ''
                if not c == '\0':
                    segs = []
                    if c in '─┼┬┴':  segs.append((0, 1,  2, 1))
                    if c in '│┼├┤':  segs.append((1, 0,  1, 2))
                    if c in '├┌└':   segs.append((1, 1,  2, 1))
                    if c in '┤┐┘':   segs.append((0, 1,  1, 1))
                    if c in '┬┌┐':   segs.append((1, 1,  1, 2))
                    if c in '┴└┘':   segs.append((1, 0,  1, 1))
                    if c in '╱╳':    segs.append((0, 2,  2, 0))
                    if c in '╲╳':    segs.append((0, 0,  2, 2))
                    if c in '←':
                        segs.append((0, 1,  1.9, 1))
                        segs.append((1, 0.6,  0, 1))
                        segs.append((1, 1.4,  0, 1))
                    elif c in '→':
                        segs.append((0, 1,  1.9, 1))
                        segs.append((1.1, 0.6,  1.9, 1))
                        segs.append((1.1, 1.4,  1.9, 1))
                    elif c in '↑':
                        segs.append((1, 0.4,  1, 1.8))
                        segs.append((0.3, 0.9,  1, 0.4))
                        segs.append((1.7, 0.9,  1, 0.4))
                    elif c in '↓':
                        segs.append((1, 0.4,  1, 1.8))
                        segs.append((0.3, 1.3,  1, 1.8))
                        segs.append((1.7, 1.3,  1, 1.8))
                    segs_ = []
                    for seg in segs:
                        (x1, y1, x2, y2) = [c / 2 for c in seg]
                        x1, x2 = x1 * w, x2 * w
                        y1, y2 = y1 * h, y2 * h
                        segs_.append((int(x1) + x, int(y1) + y_, int(x2) + x, int(y2) + y_))
                    if clear is not None:
                        self.change_colour(self.background)
                        self.window.fill_rectangle(self.gc, x, clear_y, w + 1, line_height)
                        self.gc.change(foreground = fc, background = bc)
                    self.window.poly_segment(self.gc, segs_)
                    x += w + 1
            else:
                buf += c
    
    def draw_coloured_text(self, x, y, ascent, descent, text):
        '''
        Draw a coloured multi-line text
        
        @param  x:int        The left position of the text
        @param  y:int        The Y position of the bottom of the text
        @param  ascent:int   Extra height above the text on each line
        @param  descent:int  Extra height under the text on each line
        @param  text:str     The text to draw
        '''
        buf, bc, fc, xx, reverse = '', self.background, self.foreground, x, False
        line_height = ascent + self.font_height + descent
        esc = False
        for c in text + '\033[m':
            if esc:
                buf += c
                if ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (c == '~'):
                    if (buf[0] == '[') and (buf[-1] == 'm'):
                        buf = buf[1 : -1].split(';')
                        buf = [int('0' + x) for x in buf]
                        bci, fci = 0, 0
                        for b in buf:
                            if not bci == 0:
                                if bci == 1:
                                    if not b == 2:
                                        bci = -2
                                    bc = 0
                                elif bci > 1:
                                    bc = (bc << 8) + b
                                    if bci == 4:
                                        bci = -1
                                        bc = (bc >> 16) & 255, (bc >> 8) & 255, bc & 255
                                        bc = self.create_colour(*bc)
                                bci += 1
                            elif not fci == 0:
                                if fci == 1:
                                    if not b == 2:
                                        fci = -2
                                    fc = 0
                                elif fci > 1:
                                    fc = (fc << 8) + b
                                    if fci == 4:
                                        fci = -1
                                        fc = ((fc >> 16) & 255, (fc >> 8) & 255, fc & 255)
                                        fc = self.create_colour(*fc)
                                fci += 1
                            elif b == 0:           bc, fc, reverse = self.background, self.foreground, False
                            elif b == 39:          fc = self.foreground
                            elif b == 49:          bc = self.background
                            elif 30 <= b <= 37:    fc = self.palette[b - 30]
                            elif 40 <= b <= 47:    bc = self.palette[b - 40]
                            elif 90 <= b <= 97:    fc = self.palette[b - 90 + 8]
                            elif 100 <= b <= 107:  bc = self.palette[b - 100 + 8]
                            elif b == 38:          fci = 1
                            elif b == 48:          bci = 1
                            elif b == 7:           reverse = True
                            elif b == 27:          reverse = False
                    buf = ''
                    esc = False
            elif c in ('\033', '\n'):
                if not buf == '':
                    self.change_colour(bc if not reverse else fc)
                    h = self.font_height + ascent
                    w = self.font_width * len(buf)
                    colours = (fc, bc) if not reverse else (bc, fc)
                    self.draw_text(x, y + ascent, descent, buf, colour = colours, clear = (y - h, line_height))
                    x += w
                    buf = ''
                if c == '\n':
                    y += line_height
                    x = xx
                else:
                    esc = True
            else:
                buf += c
        self.change_colour(self.foreground)
    
    def draw_coloured_splitted_text(self, x, width, y, ascent, descent, text):
        '''
        Draw a coloured multi-line, multi-column text
        
        @param  x:int        The left position of the text
        @param  width:int    The width of the print area
        @param  y:int        The Y position of the bottom of the text
        @param  ascent:int   Extra height above the text on each line
        @param  descent:int  Extra height under the text on each line
        @param  text:str     The text to draw, '\0' is column delimiter inside each line
        '''
        line_height = ascent + self.font_height + descent
        for line in text.split('\n'):
            if '\0' not in line:
                self.draw_coloured_text(x, y, ascent, descent, line)
            else:
                parts = line.split('\0')
                i, n = 0, len(parts) - 1
                for part in parts:
                    x = (width - Bar.coloured_length(part) * self.font_width) * i / n
                    self.draw_coloured_text(int(x), y, ascent, descent, part)
                    i += 1
            y += line_height
    
    def create_colour(self, red, green, blue):
        '''
        Create a colour instance
        
        @param   red:int    The red component [0, 255]
        @param   green:int  The green component [0, 255]
        @param   blue:int   The blue component [0, 255]
        @return             The colour
        '''
        cid = (red << 16) | (green << 8) | blue
        if cid in self.cmap_cache:
            return self.cmap_cache[cid]
        rc = self.cmap.alloc_color(red * 257, green * 257, blue * 257).pixel
        self.cmap_cache[cid] = rc
        return rc
    
    def create_font(self, font):
        '''
        Create a font
        
        @param   font:str  The font
        @return            The font, font metrics, and font height
        '''
        font = display.open_font(font)
        font_metrics = font.query()
        font_height = font_metrics.font_ascent + font_metrics.font_descent
        return (font, font_metrics, font_height)
    
    def change_colour(self, colour):
        '''
        Change the current colour
        
        @param  colour  The colour
        '''
        self.gc.change(foreground = colour)
    
    def change_font(self, font):
        '''
        Change the current font
        
        @param  font  The font
        '''
        self.gc.change(font = font)
    
    def partial_clear(self, x, width, y, ascent, descent, text):
        '''
        Fill the panel with its background colour on areas that are not
        about to be over painted with text and reset the colour and font
        
        @param  x:int        The left position of the text
        @param  width:int    The width of the print area
        @param  y:int        The Y position of the bottom of the text
        @param  ascent:int   Extra height above the text on each line
        @param  descent:int  Extra height under the text on each line
        @param  text:str     The text to draw, '\0' is column delimiter inside each line
        '''
        line_height, areas = ascent + self.font_height + descent, []
        y -= self.font_height - ascent
        
        for line in text.split('\n'):
            if '\0' not in line:
                x_ = Bar.coloured_length(line)
                if width > x_:
                    areas.append((x + x_, y, width - x_, line_height))
            else:
                areas_ = []
                parts = line.split('\0')
                i, n = 0, len(parts) - 1
                for part in parts:
                    w = Bar.coloured_length(part) * self.font_width
                    x_ = int((width - w) * i / n)
                    if w >= 0:
                        areas_.append((x_, x_ + w))
                    i += 1
                x1 = areas_[0][1]
                for x2, x3 in areas_[1:]:
                    if x2 > x1:
                        areas.append((x + x1, y, x2 - x1, line_height))
                    x1 = x3
            y += line_height
        
        self.change_colour(self.background)
        self.window.poly_fill_rectangle(self.gc, areas)
        self.change_colour(self.foreground)
        self.change_font(self.font)
    
    def clear_rectangle(self, x, y, width, height):
        '''
        Clear a rectangle on the panel
        
        @param  x:int       The X-component of the coordinate of the rectangle's top left corner
        @param  y:int       The Y-component of the coordinate of the rectangle's top left corner
        @param  width:int   The width of the rectangle
        @param  height:int  The height of the rectangle
        '''
        self.change_colour(self.background)
        self.window.fill_rectangle(self.gc, 0, 0, self.width, self.panel_height)
        self.change_colour(self.foreground)
        self.change_font(self.font)
    
    def clear(self):
        '''
        Fill the panel with its background colour and reset the colour and font
        '''
        self.clear_rectangle(0, 0, self.width, self.panel_height)
    
    def invalidate(self):
        '''
        Cause the window to be redraw on the main window
        '''
        # Dummy event for performing update in the main thread # TODO do this better
        e = Xlib.protocol.event.KeyPress(detail = 1,
                                         time = Xlib.X.CurrentTime,
                                         root = display.screen().root,
                                         window = self.window,
                                         child = Xlib.X.NONE,
                                         root_x = 1, root_y = 1,
                                         event_x = 1, event_y = 1,
                                         state = 0, same_screen = 1)
        display.send_event(self.window, e)
        display.flush()
    
    @staticmethod
    def coloured_length(text):
        '''
        The print length of a coloured text
        
        @param   text:str  The text
        @return  :int      The print length of the text
        '''
        n = 0
        esc = False
        for c in text:
            if esc:
                if ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (c == '~'):
                    esc = False
            elif c == '\033':
                esc = True
            else:
                n += 1
        return n


## Set process title
setproctitle(sys.argv[0])


## Read command line arguments
parser = ArgParser('A highly extensible minimalistic dock panel',
                   sys.argv[0] + ' [options] [-- configuration-options]',
                   None, None, True, ArgParser.standard_abbreviations())

parser.add_argumented(['-c', '--configurations'], 0, 'FILE', 'Select configuration file')
parser.add_argumentless(['-h', '-?', '--help'], 0, 'Print this help information')
parser.add_argumentless(['-C', '--copying', '--copyright'], 0, 'Print copyright information')
parser.add_argumentless(['-W', '--warranty'], 0, 'Print non-warranty information')
parser.add_argumentless(['-v', '--version'], 0, 'Print program name and version')

parser.parse()
parser.support_alternatives()

if parser.opts['--help'] is not None:
    parser.help()
    sys.exit(0)
elif parser.opts['--copyright'] is not None:
    print(copyright[1 : -1])
    sys.exit(0)
elif parser.opts['--warranty'] is not None:
    print(copyright.split('\n\n')[2])
    sys.exit(0)
elif parser.opts['--version'] is not None:
    print('%s %s' % (PROGRAM_NAME, PROGRAM_VERSION))
    sys.exit(0)

a = lambda opt : opt[0] if opt is not None else None
config_file = a(parser.opts['--configurations'])


## Load extension and configurations via xpybarrc
if config_file is None:
    dirs = os.environ['XDG_CONFIG_DIRS'].split(':') if 'XDG_CONFIG_DIRS' in os.environ else []
    files = ['$XDG_CONFIG_DIRS/%rc'] * len(dirs)
    files = ['$XDG_CONFIG_HOME/%/%rc', '$HOME/.config/%/%rc', '$HOME/.%rc',
             '$~/.config/%/%rc', '$~/.%rc'] + files + ['/etc/%rc']
    home = pwd.getpwuid(os.getuid()).pw_dir.replace('$', '\0')
    for file in files:
        file = file.replace('%', 'xpybar')
        for arg in ('XDG_CONFIG_HOME', 'XDG_CONFIG_DIRS', 'HOME', '~'):
            if '$' + arg in file:
                if arg == 'XDG_CONFIG_DIRS':
                    dir, dirs = dirs[0].replace('$', '\0'), dirs[1:]
                    file = file.replace('$' + arg, dir)
                elif arg == '~':
                    file = file.replace('$' + arg, home)
                elif arg in os.environ:
                    file = file.replace('$' + arg, os.environ[arg].replace('$', '\0'))
                else:
                    file = None
                    break
        if file is not None:
            file = file.replace('\0', '$')
            if os.path.exists(file):
                config_file = file
                break
conf_opts = [config_file] + parser.files
if config_file is not None:
    code = None
    with open(config_file, 'rb') as script:
        code = script.read()
    code = code.decode('utf-8', 'strict') + '\n'
    code = compile(code, config_file, 'exec')
    g, l = globals(), dict(locals())
    for key in l:
        g[key] = l[key]
    exec(code, g)
else:
    print('No configuration file found')
    sys.exit(1)


open_x()
display = get_display()
outputs = get_monitors()
start()

while True:
    try:
        e = display.next_event()
        if e.type == Xlib.X.DestroyNotify:
            break
        else:
            unhandled_event(e)
    except KeyboardInterrupt:
        break
    redraw()
    display.flush()

stop()
close_x()

