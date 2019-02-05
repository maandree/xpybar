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


class DentryState:
    '''
    Data from /proc/sys/fs/dentry-state
    
    Information about the status of the directory cache (dcache)
    
    @variable  nr_dentry:int   Number of allocated directory entries
    @variable  nr_unused:int   Number of unused directory entries
    @variable  age_limit:int   Age limit in seconds
    @variable  want_pages:int  Pages requested by the system
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        state = None
        with open('/proc/sys/fs/dentry-state', 'rb') as file:
            state = file.read()
        state = state.decode('utf-8', 'replace').replace('\t', ' ')
        state = [int(field) for field in state.split(' ') if not field == '']
        (self.nr_dentry, self.nr_unused, self.age_limit, self.want_pages, _dummy1, _dummy_2) = state

