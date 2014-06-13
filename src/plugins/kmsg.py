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

from plugins.linereader import LineReader



class KMsg(LineReader):
    '''
    Line reader for the kernel console output
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        LineReader.__init__(self, '/dev/kmsg')
        self.__first = True
    
    
    def next(self):
        '''
        Reads the next line
        
        @return  :str?  The next line, `None` if stream has closed
        '''
        try:
            if self.__first:
                import time
                self.__first = False
                while True:
                    start = time.monotonic()
                    rc = LineReader.next(self)
                    end = time.monotonic()
                    if end - start > 1:
                        return rc
            else:
                return LineReader.next(self)
        except:
            return None

