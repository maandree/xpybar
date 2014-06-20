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


class InodeState:
    '''
    Data from /proc/sys/fs/inode-state
    
    @variable  nr_inodes:int        The number of inodes the system has allocated.
                                    This can be slightly more than inode-max because
                                    Linux allocates them one page full at a time.
    @variable  nr_free_inodes:int   The number of free inodes
    @variable  preshrink:int        Nonzero when the `nr_inodes` is more than inode-max
                                    and the system needs to prune the inode list instead
                                    of allocating more
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        state = None
        with open('/proc/sys/fs/inode-state', 'rb') as file:
            state = file.read()
        state = state.decode('utf-8', 'replace').replace('\t', ' ')
        state = [int(field) for field in state.split(' ') if not field == '']
        (self.nr_inodes, self.nr_free_inodes, self.preshrink, _dummy1, _dummy2, _dummy_3, _dummy_4) = state

