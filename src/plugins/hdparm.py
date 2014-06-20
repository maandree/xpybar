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

from util import *


class HDParm: # TODO add output parsers
    '''
    Set/get SATA/IDE device parameters
    '''
    
    
    READAHEAD_SECTOR_COUNT = 'a'
    HAVE_READAHEAD = 'A'
    ADVANCED_POWER_MANAGEMENT = 'B'
    IDE_32BIT_IO_SUPPORT = 'c'
    POWER_MODE_STATUS = 'C'
    GEOMETRY = 'g'
    HITACHI_TEMPERATURE = 'H'
    KERNEL_INFORMATION = 'i'
    DIRECT_INFORMATION = 'I'
    WESTERN_DIGITAL_IDLE3_TIMEOUT = 'J'
    MULTIPLE_SECTOR_IO_SECTOR_COUNT = 'm'
    AUTOMATIC_ACOUSTIC_MANAGEMENT = 'M'
    MAX_VISIBLE_SECTOR_COUNT = 'N'
    COMMAND_QUEUE_DEPTH = 'Q'
    IS_READONLY = 'r'
    HAVE_WRITE_READ_VERIFY = 'R'
    IDLE_MODE = 'S'
    HAVE_WRITE_CACHING = 'W'
    STANDBY_MODE = 'y'
    SLEEP_MODE = 'Y'
    DISABLE_SEAGATE_AUTOMATIC_POWER_SAVING = 'Z'
    
    
    def __init__(self, devices = None):
        '''
        Constructor
        
        @param  devices:list<str>?  The devices to use, `None` for all
        '''
        self.devices = HDParm.get_devices() if devices is None else self.devices
        spawn_read()
    
    
    def get(self, action):
        '''
        Read information about selected devices
        
        @param   action:str  The information to read
        @return  :str        The read information
        '''
        return spawn_read('restricted-hdparm', '-%s' % action)
    
    
    def set(self, action, value = None):
        '''
        Configure selected devices
        
        @param   action:str  The settings to reconfigure
        @param   value:int?  The value to apply, `None` if there is no value to apply
        @return  :str        The read information
        '''
        if value is None:
            spawn('restricted-hdparm', action)
        else:
            spawn('restricted-hdparm', '-%s%s' % (action, str(value)))
    
    
    @staticmethod
    def get_devices(self):
        '''
        List available devices
        
        @param  :list<str>  Available devices
        '''
        test = lambda dev : (len(dev) == 3) and (dev[:2] in ('sd', 'hd'))
        return filter(test, os.listdir('/dev'))

