# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016  Mattias Andrée (maandree@member.fsf.org)

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


class SNMP:
    '''
    IPv4 SNMP data
    
    @variable  keys:list<str>  List of avaiable keys
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        snmp = None
        with open('/proc/net/snmp', 'rb') as file:
            snmp = file.read()
        snmp = snmp.decode('utf-8', 'replace')
        
        filter_ = lambda array : filter(lambda x : not x == '', array)
        snmp = list(map(lambda x : x.split(' '), filter_(snmp.split('\n'))))
        snmp_h = filter(lambda i : i % 2 == 0, range(len(snmp)))
        snmp_d = filter(lambda i : i % 2 == 1, range(len(snmp)))
        snmp_h = list(map(lambda i : snmp[i], snmp_h))
        snmp_d = list(map(lambda i : snmp[i], snmp_d))
        snmp = zip(snmp_h, snmp_d)
        
        self.__info = {}
        self.keys = []
        for header_list, data_list in snmp:
            prefix = header_list[0][:-1]
            for suffix, value in zip(header_list[1:], data_list[1:]):
                key = prefix + suffix
                self.__info[key] = int(value)
                self.keys.append(key)
    
    
    def __contains__(self, key):
        '''
        Get whether or not a key is available
        
        @param   key:str  The key
        @return  :bool    The availability
        '''
        return key in self.__info
    
    
    def __getitem__(self, key):
        '''
        Lookup a field from '/proc/net/snmp'
        
        @param   key:str  The field name
        @return  :int     The value of the field
        '''
        return self.__info[key]

