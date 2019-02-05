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


class Random:
    '''
    Entropy pool status
    
    @variable  poolsize:int                 The size of the entropy pool, see `man 4 random` for more information
    @variable  read_wakeup_threshold:int    The number of bits of entropy required for waking up processes
                                            that sleep waiting for entropy from `/dev/random`
    @variable  write_wakeup_threshold:int   The number of bits of entropy below which we wake up processes
                                            that do a `select` or `poll` for write access to `/dev/random`
    @variable  urandom_min_reseed_secs:int  The minimum number of seconds between urandom pool reseeding
    @variable  boot_id:int                  Random UUID generated when the system is booted
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        def read(filename):
            with open('/proc/sys/kernel/random/' + filename, 'rb') as file:
                return file.read().decode('utf-8', 'replace').rstrip('\n')
        
        self.poolsize                = int(read('poolsize'))
        self.read_wakeup_threshold   = int(read('read_wakeup_threshold'))
        self.write_wakeup_threshold  = int(read('write_wakeup_threshold'))
        self.urandom_min_reseed_secs = int(read('urandom_min_reseed_secs'))
        self.boot_id                 =     read('boot_id')
    
    
    def entropy_avail(self):
        '''
        Get the number of bits available in the entropy pool.
        Note that `poolsize` is in bytes on Linux<2.6.
        
        @return  :int  The number of bits available in the entropy pool
        '''
        with open('/proc/sys/kernel/random/entropy_avail', 'rb') as file:
            return int(file.read().decode('utf-8', 'replace').rstrip('\n'))

