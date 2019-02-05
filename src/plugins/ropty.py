# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016, 2017, 2018, 2019  Mattias Andrée (maandree@kth.se)

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
import threading

from plugins.linereader import LineReader


class ROPTY(LineReader):
    '''
    Read-only PTY for viewing of wall, write and talk messages
    
    @variable  on_update:()→void  Called when a new line is available
    @variable  master:int         The file descriptor of the PTY master
    @variable  slave:int          The file descriptor of the PTY slave
    '''
    
    
    def __init__(self, on_update = None):
        '''
        Constructor
        
        @param  on_update:()→void  Called when a new line is available
        '''
        def noop():
            pass
        self.on_update = noop if on_update is None else on_update
        (self.master, self.slave) = os.openpty()
        self.__reader = LineReader(self.master)
        self.__condition = threading.Condition()
        self.__queue = []
        def background():
            try:
                while True:
                    got = self.__reader.next()
                    if got is None:
                        return
                    self.__condition.acquire()
                    try:
                        self.__queue.append(got)
                    finally:
                        self.__condition.release()
                    self.on_update()
            except:
                return
        self.__thread = threading.Thread(target = background)
        self.__thread.setDaemon(True)
        self.__thread.start()
    
    
    def close(self):
        '''
        Close the PTY
        '''
        os.close(self.slave)
        os.close(self.master)
    
    
    def size(self):
        '''
        Return the number of available lines
        
        @return  :int  The number of available lines
        '''
        self.__condition.acquire()
        try:
            return len(self.__queue)
        finally:
            self.__condition.release()
    
    
    def __len__(self):
        '''
        Return the number of available lines
        
        @return  :int  The number of available lines
        '''
        return self.size()
    
    
    def next(self):
        '''
        Return and unqueue the next available line
        
        @return  :str  The next available line, `None` if there
                       are no more lines currently available
        '''
        self.__condition.acquire()
        try:
            if len(self.__queue) == 0:
                return None
            rc = self.__queue[0]
            self.__queue[:] = self.__queue[1:]
        finally:
            self.__condition.release()
        return rc

