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

import os


class XDisplay:
    '''
    Retrieve information about the used X display
    
    @variable  connection:str?  The full X display information, `None` if X is not running
    @variable  host:str?        The host, often `None` one local conncetions and "localhost" on remote oonnection
    @variable  display:int      The display number
    @variable  screen:int?      The screen number , often `None`
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        self.connection = os.environ['DISPLAY'] if 'DISPLAY' in os.environ else None
        self.host = self.connection.split(':')[0]
        if self.host == '':
            self.host = None
        self.display, self.screen = (self.connection.split(':')[1] + '.').split('.')[:2]
        self.display = int(self.display)
        self.screen = None if self.screen == '' else int(self.screen)
