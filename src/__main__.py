#!/usr/bin/env python3
copyright = '''
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
from argparser import *

from x import *
from util import *


global OUTPUT, HEIGHT, YPOS, TOP, FONT, BACKGROUND, FOREGROUND
global dislay, outputs, redraw, Bar, start, stop
global conf_opts, config_file, parser

OUTPUT, HEIGHT, YPOS, TOP = 0, 12, 0, True
FONT = '-misc-fixed-*-*-*-*-10-*-*-*-*-*-*-*'
BACKGROUND, FOREGROUND = (0, 0, 0), (192, 192, 192)


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
    '''
    
    def __init__(self, output, height, ypos, top, font, background, foreground):
        '''
        Constructor
        
        @param  output:int                                 The index of the output within the screen as printed by xrandr, except primary is first
        @param  height:int                                 The height of the panel
        @param  ypos:int                                   The position of the panel in relation the either the top or bottom edge of the output
        @param  top:int                                    Whether the panel is to be docked to the top of the output, otherwise to the bottom
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
        self.background = self.create_colour(*background)
        self.foreground = self.create_colour(*foreground)
        (self.font, self.font_metrics, self.font_height) = self.create_font(font)
    
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
        return self.font.query_text_extents(text).overall_width
    
    def draw_text(self, x, y, text):
        '''
        Draw a text
        
        @param  x:int     The left position of the text
        @param  y:int     The Y position of the bottom of the text
        @param  text:str  The text to draw
        '''
        draw_text(bar.window, bar.gc, x, y, text)
    
    # TODO add draw_coloured_text
    
    def create_colour(self, red, green, blue):
        '''
        Create a colour instance
        
        @param   red:int    The red component [0, 255]
        @param   green:int  The green component [0, 255]
        @param   blue:int   The blue component [0, 255]
        @return             The colour
        '''
        return self.cmap.alloc_color(red * 257, green * 257, blue * 257).pixel
    
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
    
    def clear(self):
        '''
        Fill the panel with its background colour and reset the colour and font
        '''
        self.change_colour(self.background)
        self.window.fill_rectangle(self.gc, 0, 0, self.width, self.panel_height)
        self.change_colour(self.foreground)
        self.change_font(self.font)


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
    print('This program is distributed in the hope that it will be useful,')
    print('but WITHOUT ANY WARRANTY; without even the implied warranty of')
    print('MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the')
    print('GNU Affero General Public License for more details.')
    sys.exit(0)
elif parser.opts['--version'] is not None:
    print('%s %s' % (PROGRAM_NAME, PROGRAM_VERSION))
    sys.exit(0)

a = lambda opt : opt[0] if opt is not None else None
config_file = a(parser.opts['--configurations'])


## Load extension and configurations via xpybarrc
if config_file is None:
    for file in ('$XDG_CONFIG_HOME/%/%rc', '$HOME/.config/%/%rc', '$HOME/.%rc', '/etc/%rc'):
        file = file.replace('%', 'xpybarrc')
        for arg in ('XDG_CONFIG_HOME', 'HOME'):
            if '$' + arg in file:
                if arg in os.environ:
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
    code = code.decode('utf-8', 'error') + '\n'
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

