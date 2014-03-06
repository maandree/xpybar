# -*- python -*-
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

import Xlib.XK


class XKB:
    '''
    X keyboard monitor
    '''
    
    
    NUM = 1
    '''
    :int  The bit in `get_locks` representing Num Lock
    '''
    
    CAPS = 2
    '''
    :int  The bit in `get_locks` representing Royal Canterlot Voice
    '''
    
    SCROLL = 4
    '''
    :int  The bit in `get_locks` representing Scroll Lock
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        self.__root = get_screen().root
        
        lockkey = lambda lock : self.__display.keysym_to_keycode(Xlib.XK.string_to_keysym(lock + '_Lock'))
        find    = lambda array, item : (1 << array.index(item)) if item in array else -1
        mods    = [x[0] for x in get_display().get_modifier_mapping()]
        
        self.__num    = find(mods, lockkey('Num'))
        self.__caps   = find(mods, lockkey('Caps'))
        self.__scroll = find(mods, lockkey('Scroll'))
    
    
    def get_locks(self):
        '''
        Get the currently active lock keys (num lock, caps lock and scroll lock, but not compose)
        
        @return  :int  The bitwise OR of the active lock keys (XKB.NUM, XKB.CAPS, XKB.SCROLL)
        '''
        # TODO add update listener
        mask = self.__root.query_pointer().mask
        rc = 0
        rc |= XKB.NUM    if (mask & self.__num)    == self.__num    else 0
        rc |= XKB.CAPS   if (mask & self.__caps)   == self.__caps   else 0
        rc |= XKB.SCROLL if (mask & self.__scroll) == self.__scroll else 0
        return rc

