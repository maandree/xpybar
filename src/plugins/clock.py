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

import time
from datetime import datetime, timezone

from util import *


class Clock:
    '''
    Date and time information retrieval
    '''
    
    
    SECONDS = 1
    '''
    :float  Synchronisation value for syncing to seconds
    '''
    
    MINUTES = 60
    '''
    :float  Synchronisation value for syncing to minutes
    '''
    
    
    def __init__(self, format = '%Y-(%m)%b-%d %T, %a w%V, %Z', utc = False, sync_to = 1):
        '''
        Constructor
        
        @param  format:str     The format as in the `date` command
        @param  utc:bool       Show time in UTC, otherwise local time
        @param  sync_to:float  The time parameter to sync to, the number of seconds between the reads
        '''
        self.format = format if not utc else format.replace('%Z', 'UTC')
        self.utc = utc
        self.sync_to = sync_to
    
    
    def read(self):
        '''
        Reads the clock
        
        @return  :str  The time and date in the format specified at construction
        '''
        if not self.utc:
            return time.strftime(self.format)
        else:
            return datetime.fromtimestamp(time.time(), tz = timezone.utc).strftime(self.format)
    
    
    def sync(self):
        '''
        Wait for the clock to reach the next synchronisation time point
        '''
        time.sleep(self.sync_to - (time.time() % self.sync_to))
    
    
    def continuous_sync(self, function):
        '''
        Wait for the clock to reach the next synchronisation time point
        and the call a function and start over, i.e. sync in a loop forever
        
        @param  function:()→void  The function to call
        '''
        while True:
            time.sleep(self.sync_to - (time.time() % self.sync_to))
            function()
    
    
    @staticmethod
    def posix_time():
        '''
        Returns the current POSIX time
        
        @return  :float  The current POSIX time
        '''
        return time.time()

