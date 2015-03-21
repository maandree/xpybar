# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015  Mattias Andrée (maandree@member.fsf.org)

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


class SoftIRQs:
    '''
    Data from /proc/softirqs
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        softirqs = None
        with open('/proc/softirqs', 'rb') as file:
            softirqs = file.read()
        softirqs = softirqs.decode('utf-8', 'replace')
        
        filter_ = lambda array : filter(lambda x : not x == '', array)
        softirqs = map(lambda x : x.split(' '), filter_(softirqs.split('\n')[1:]))
        
        self.__info = {}
        for line in softirqs:
            self.__info[line[0][:-1]] = [int(x) for x in line[1:]]
    
    
    def __contains__(self, key):
        '''
        Get whether or not a key is available
        
        @param   key:str  The key
        @return  :bool    The availability
        '''
        return key in self.__info
    
    
    def __getitem__(self, key):
        '''
        Lookup a field from '/proc/softirqs'
        
        @param   key:str     The field name
        @return  :list<int>  The value of the field, for each processor
        '''
        return self.__info[key]

