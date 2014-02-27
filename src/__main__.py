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


open_x()
display = get_display()
outputs = get_monitors()
bar = Bar(OUTPUT, HEIGHT, YPOS, TOP, FONT, BACKGROUND, FOREGROUND)

bar.map()

while True:
    try:
        e = display.next_event()
        if e.type == Xlib.X.DestroyNotify:
            break
    except KeyboardInterrupt:
        break
    bar.clear()
    bar.draw_text(0, 10, '°°° TEST °°°')
    display.flush()

bar.unmap()
close_x()

