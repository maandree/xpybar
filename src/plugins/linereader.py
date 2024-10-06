# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016, 2017, 2018, 2019  Mattias Andrée (m@maandreese)

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
from util import *


class LineReader:
    '''
    Line reader
    '''
    
    
    def __init__(self, channel = None):
        '''
        Constructor
        
        @param  channel:str|int|istream?  The pathname, file descriptor or stream
                                          of the file to read, `None` for stdin
        '''
        self.__channel = None
        if channel is None:
            self.__next = lambda : input()
        else:
            next__ = lambda : channel.read(1)
            if isinstance(channel, str):
                self.__channel = channel = os.open(channel, os.O_RDONLY)
            if isinstance(channel, int):
                channel = os.fdopen(channel)
                next__ = lambda : channel.read(1)
            buffer = ''
            def next_():
                nonlocal buffer
                while True:
                    got = next__()
                    if (got is None) or (len(got) == 0):
                        return None
                    if not isinstance(got, str):
                        got = got.decode('utf-8', 'replace')
                    buffer += got
                    if '\n' in buffer:
                        got = buffer.find('\n')
                        got, buffer = buffer[:got], buffer[got + 1:]
                        return got
            self.__next = next_
    
    
    def next(self):
        '''
        Reads the next line
        
        @return  :str?  The next line, `None` if stream has closed
        '''
        try:
            return self.__next()
        except:
            return None
    
    
    def close(self):
        '''
        Close any file this object has opened
        '''
        if self.__channel is not None:
            os.close(self.__channel)
    
    
    def __enter__(self):
        '''
        Invoked when `with` enters
        '''
        return self
    
    
    def __exit__(self, _type, _value, _trace):
        '''
        Invoked when `with` exits
        '''
        self.close()

