# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015  Mattias Andrée (maandree@member.fsf.org)

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


class Menu:
    '''
    Dropdown menu

    Instances of this class is compatible with `Bar`
    
    You should extend the global function `stop` to unmap any menu that
    is still open at the time that function is called
    
    @variable  window            The X window
    @variable  gc                The window's graphics context
    @variable  cmap              The window's colour map
    @variable  width:int         The menu's pixel width
    @variable  height:int        The output's pixel height
    @variable  left:int          The output's left position
    @variable  top:int           The output's top position
    @variable  ypos:int          The position of the menu in relation to either the top or bottom edge of the output
    @variable  panel_height:int  The menu's height, note that the name is `panel_height` for compatibility with `Bar`
    @variable  at_top:bool       Whether the menu is to be positioned relative the top of the output, otherwise to the bottom
    @variable  background        The default background
    @variable  foreground        The default foreground
    @variable  font              The default font
    @variable  font_metrics      The default font's metrics
    @variable  font_height:int   The height of the default font
    @variable  font_width:int    The width of an 'X' with the default font
    @variable  palette           A 16-array of standard colours
    @variable  cmap_cache        Custom colour map cache
    '''
    
    
    methods_set = False
    '''
    :bool  Indicates whether a constructor has set methods common with `Bar`
    '''
    
    
    def __init__(self, output, width, height, xpos, ypos, left, top, font = None,
                 background = None, foreground = None, event_mask = None, override_redirect = True):
        '''
        Constructor
        
        @param  output:int                                  The index of the output within the screen as printed by xrandr, except primary is first
        @param  width:int                                   The width of the menu
        @param  height:int                                  The height of the menu
        @param  xpos:int                                    The position of the menu in relation the either the left or right edge of the output
        @param  ypos:int                                    The position of the menu in relation the either the top or bottom edge of the output
        @param  left:int                                    Whether the menu is positioned relative to the left of the output, otherwise to the right
        @param  top:int                                     Whether the menu is positioned relative to the top of the output, otherwise to the bottom
        @param  font:str?                                   The default font, `None` for the default
        @param  background:(red:int, green:int, blue:int)?  The default background, `None` for the default
        @param  foreground:(red:int, green:int, blue:int)?  The default foreground, `None` for the default
        @param  event:int?                                  Mask of events that should be caught, `None` for the default
        @param  override_redirect:bool                      Whether override_redirect should be set
        '''
        import os
        import Xlib.display, Xlib.Xatom, Xlib.ext.randr, Xlib.X
        
        if not Menu.methods_set:
            Menu.map                         = Bar.map
            Menu.unmap                       = Bar.unmap
            Menu.text_width                  = Bar.text_width
            Menu.draw_text                   = Bar.draw_text
            Menu.draw_coloured_text          = Bar.draw_coloured_text
            Menu.draw_coloured_splitted_text = Bar.draw_coloured_splitted_text
            Menu.create_colour               = Bar.create_colour
            Menu.create_font                 = Bar.create_font
            Menu.change_colour               = Bar.change_colour
            Menu.change_font                 = Bar.change_font
            Menu.clear_rectangle             = Bar.clear_rectangle
            Menu.clear                       = Bar.clear
            Menu.invalidate                  = Bar.invalidate
            Menu.coloured_length             = Bar.coloured_length
            Menu.methods_set = True
        
        if event_mask is None:
            event_mask = ( Xlib.X.StructureNotifyMask
                         | Xlib.X.ButtonPressMask
                         | Xlib.X.ButtonReleaseMask
                         | Xlib.X.ExposureMask
                         | Xlib.X.KeyPress
                         | Xlib.X.KeyRelease
                         | Xlib.X.MotionNotify
                         | Xlib.X.EnterNotify
                         | Xlib.X.LeaveNotify
                         )
        if font       is None:  font       = FONT
        if background is None:  background = BACKGROUND
        if foreground is None:  foreground = FOREGROUND
        
        [self.width, self.height, self.left, self.top] = outputs[output][:4]
        [self.ypos, self.panel_height, self.at_top] = [ypos, height, top]
        self.left += xpos if left else (self.width - xpos - width)
        self.top += ypos if top else (self.height - ypos - height)
        self.width = width
        
        self.window = screen.root.create_window(self.left, self.top, self.width, self.panel_height, 0,
                                                Xlib.X.CopyFromParent,
                                                Xlib.X.InputOutput,
                                                Xlib.X.CopyFromParent,
                                                event_mask = event_mask,
                                                colormap = Xlib.X.CopyFromParent,
                                                override_redirect = override_redirect)
        
        self.window.set_wm_name('xpybar')
        self.window.set_wm_icon_name('xpybar')
        self.window.set_wm_class('menu', 'xpybar')
        self.window.set_wm_client_machine(os.uname().nodename)
        
        _CARD    = display.intern_atom("CARDINAL")
        _DESKTOP = display.intern_atom("_NET_WM_DESKTOP")
        _PID     = display.intern_atom("_NET_WM_PID")
        self.window.change_property(_DESKTOP, _CARD, 32, [0xFFFFFFFF])
        self.window.change_property(_PID,     _CARD, 32, [os.getpid()])
        
        _ATOM   = display.intern_atom("ATOM")
        _TYPE   = display.intern_atom("_NET_WM_WINDOW_TYPE")
        _NORMAL = display.intern_atom("_NET_WM_WINDOW_TYPE_NORMAL")
        self.window.change_property(_TYPE, _ATOM, 32, [_NORMAL])
        
        self.gc = self.window.create_gc()
        self.cmap = self.window.get_attributes().colormap
        self.cmap_cache = {}
        self.background = self.create_colour(*background)
        self.foreground = self.create_colour(*foreground)
        (self.font, self.font_metrics, self.font_height) = self.create_font(font)
        self.font_width = self.text_width('X')
        self.palette = [0x000000, 0xCD656C, 0x32A679, 0xCCAD47, 0x2495BE, 0xA46EB0, 0x00A09F, 0xD8D8D8]
        self.palette += [0x555555, 0xEB5E6A, 0x0EC287, 0xF2CA38, 0x00ACE0, 0xC473D1, 0x00C3C7, 0xEEEEEE]
        self.palette = [((p >> 16) & 255, (p >> 8) & 255, p & 255) for p in self.palette]
        self.palette = [self.create_colour(*p) for p in self.palette]

