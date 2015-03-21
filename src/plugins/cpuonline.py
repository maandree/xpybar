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


class CPUOnline:
    '''
    Online CPU listing
    
    @variable  offline:list<int>   Offline CPU:s
    @variable  online:list<int>    Online CPU:s
    @variable  possible:list<int>  Possible CPU:s
    @variable  present:list<int>   Present CPU:s
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        def expand(data):
            if '-' not in data:
                return [int(data)]
            range_ = lambda a, b : list(range(a, b + 1))
            return range_(*[int(x) for x in data.split('-')])
        
        data = []
        for filename in ('offline', 'online', 'possible', 'present'):
            with open('/sys/devices/system/cpu/online', 'rb') as file:
                data.append(file.read())
        
        data = [x.decode('utf-8', 'replace').replace('\n', ' ').replace(',', ' ') for x in data]
        data = [map(expand, filter(lambda item : not item == '', x.split(' '))) for x in data]
        data = [reduce(lambda x, y : x + y, list(x)) for x in data]
        
        (self.offline, self.online, self.possible, self.present) = data

