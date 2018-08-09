# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016, 2017, 2018  Mattias Andrée (maandree@kth.se)

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
        
        @param  :dict<str, bool>  A map from the ID:s of the lids (you probably just
                                  have one or zero) to `True` for open and `False`
                                  for closed.
        '''
        ret = {}
        for lid in os.listdir('/proc/acpi/button/lid/'):
            try:
                with open('/proc/acpi/button/lid/%s/state' % lid, 'rb') as file:
                    ret[lid] = 'open' in file.read().decode('utf-8', 'strict')
            except:
                pass
        return ret
