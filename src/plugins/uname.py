# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016, 2017  Mattias Andrée (maandree@member.fsf.org)

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


class Uname:
    '''
    Retrieve certain system information
    
    @variable  kernel_name:str         The kernel name
    @variable  nodename:str            The network node hostname
    @variable  kernel_release:str      The kernel release
    @variable  kernel_version:str      The kernel version
    @variable  machine:str             The machine hardware name
    @variable  processor:str?          The processor type, `None` if unknown
    @variable  hardware_platform:str?  The hardware platform, `None` if unknown
    @variable  operating_system:str    The operating system
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        u = lambda s : None if s == 'unknown' else s
        (self.kernel_name, self.nodename, self.kernel_release, self.kernel_version, self.machine) = os.uname()
        self.processor         = u(spawn_read('uname', '-p'))
        self.hardware_platform = u(spawn_read('uname', '-i'))
        self.operating_system  = spawn_read('uname', '-o')


