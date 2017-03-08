# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016, 2017  Mattias Andrée (maandree@member.fsf.org)

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


class Lid:
    '''
    Laptop lid monitor
    '''
    
    @staticmethod
    def is_open():
        '''
        Check whether the lid is open
        
        @param  :bool?  `True` if the lid is open,
                        `False` if the lid is closed,
                        `None` if there is no lid, or if the
                        computer does not report the lid's state
        '''
        if not os.path.exists('/proc/acpi/button/lid/LID/state'):
            return None
        with open('/proc/acpi/button/lid/LID/state', 'rb') as file:
            return 'open' in file.read().decode('utf-8', 'strict')
