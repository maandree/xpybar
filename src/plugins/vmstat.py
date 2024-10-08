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

from util import *


class VMStat:
    '''
    Various virtual memory statistics
    
    @variable  keys:list<str>  List of avaiable keys
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        vmstat = None
        with open('/proc/vmstat', 'rb') as file:
            vmstat = file.read()
        vmstat = vmstat.decode('utf-8', 'replace')
        vmstat = map(lambda x : x.split(' '), filter(lambda x : not x == '', vmstat.split('\n')))
        
        self.__info = {}
        self.keys = []
        for field, value in vmstat:
            self.__info[field] = int(value)
            self.keys.append(field)
    
    
    def __contains__(self, key):
        '''
        Get whether or not a key is available
        
        @param   key:str  The key
        @return  :bool    The availability
        '''
        return key in self.__info
    
    
    def __getitem__(self, key):
        '''
        Lookup a field from '/proc/vmstat'
        
        @param   key:str  The field name
        @return  :int     The value of the field
        '''
        return self.__info[key]

