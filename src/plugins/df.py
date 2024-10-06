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


class Discs:
    '''
    Retrieve information about mounted discs
    
    @variable  filesystems:dict<str, Disc>  Map from filesystem to disc
    @variable  mountpoints:dict<str, Disc>  Map from mountpoint to disc
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        self.filesystems = {}
        self.mountpoints = {}
        listed = {}
        
        df = spawn_read('df', '-B1', '-T').split('\n')[1:]
        dfi = spawn_read('df', '-i').split('\n')[1:]
        
        # Disc usage information
        for line in df:
            line = line
            buf = ''
            cells = []
            for c in line:
                if (c == ' ') and (len(cells) < 6):
                    if not buf == '':
                        cells.append(buf)
                        buf = ''
                else:
                    buf += c
            cells.append(buf)
            (fs, fstype, blocks, used, avail, _use, mount) = cells
            listed[fs] = mount
            disc = Disc()
            self.filesystems[fs] = disc
            self.mountpoints[mount] = disc
            disc.filesystem = fs
            disc.mountpoint = mount
            disc.fstype = fstype
            disc.blocks = int(blocks)
            disc.used = int(used)
            disc.available = int(avail)
        
        # Inode usage information
        for line in dfi:
            line = line
            buf = ''
            cells = []
            for c in line:
                if (c == ' ') and (len(cells) < 5):
                    if not buf == '':
                        cells.append(buf)
                        buf = ''
                else:
                    buf += c
            cells.append(buf)
            (fs, inodes, iused, ifree, _use, _mount) = cells
            if fs in self.filesystems:
                del listed[fs]
                disc = self.filesystems[fs]
                disc.inodes = int(inodes)
                disc.iused = int(iused)
                disc.ifree = int(ifree)
        
        # Perhaps an umount appeared between `df -B1 -T` and `df -i`
        for fs in listed.keys():
            del self.filesystems[fs]
            del self.mountpoints[listed[fs]]


class Disc:
    '''
    Information about a single disc
    
    @variable  filesystem:str  The filesystem, a device or API filesystem name
    @variable  mountpoint:str  The filesystem mountpoint, the one with shortest name if there are multiple
    @variable  fstype:str      The filesystem type
    @variable  blocks:int      The total number of 1 byte blocks, the value is close or equal to `used + available`
    @variable  used:int        The number of used bytes
    @variable  available:int   The number of unused bytes
    @variable  inodes:int      The total number of index nodes
    @variable  iused:int       The number of used index nodes
    @variable  ifree:int       The number of available index nodes
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        pass

