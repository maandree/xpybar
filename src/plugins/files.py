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


class Files:
    '''
    Data from /proc/sys/fs/file-nr
    
    @variable  nr_files:int        The number of allocated file handles, i.e.,
                                   the number of files presently opened
    @variable  nr_free_files:int   The number of free file handles
    @variable  file_max:int        The maximum number of file handles
    
    If the number of allocated file handles is close to the maximum,
    you should consider increasing the maximum. Before Linux 2.6, the
    kernel allocated file handles dynamically, but it didn't free them
    again. Instead the free file handles were kept in a list for
    reallocation; the "free file handles" value indicates the size of
    that list. A large number of free file handles indicates that there
    was a past peak in the usage of open file handles. Since Linux 2.6,
    the kernel does deallocate freed file handles, and the "free file
    handles" value is always zero.
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        state = None
        with open('/proc/sys/fs/file-nr', 'rb') as file:
            state = file.read()
        state = state.decode('utf-8', 'replace').replace('\t', ' ')
        state = [int(field) for field in state.split(' ') if not field == '']
        (self.nr_files, self.nr_free_files, self.file_max) = state

