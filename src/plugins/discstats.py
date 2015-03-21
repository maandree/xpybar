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


class DiscStats:
    '''
    Retrieve disc statistics
    
    @variable  devices:dict<str, Disc>            Map from device name to disc
    @variable  majors:dict<int, dict<int, Disc>>  Map from major to minor and then to disc
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        discstats = None
        with open('/proc/diskstats', 'rb') as file:
            discstats = file.read()
        discstats = discstats.decode('utf-8', 'replace')
        discstats = filter(lambda x : not x == '', discstats.split('\n'))
        
        self.devices, self.majors = {}, {}
        
        for line in discstats:
            line = list(filter(lambda x : not x == '', line.split(' ')))
            line = [line[i] if i == 2 else int(line[i]) for i in range(len(line))]
            disc = DiscStat(line)
            self.devices[disc.device] = disc
            if disc.major not in self.majors:
                self.majors[disc.major] = {}
            self.majors[disc.major][disc.minor] = disc


class DiscStat:
    '''
    Statistics about a single disc or partition
    
    @variable  major:int             Device major number
    @variable  minor:int             Device minor mumber
    @variable  device:str            Device name
    @variable  r_complete:int        Reads completed successfully
    @variable  r_merge:int           Reads merged
    @variable  r_sectors:int         Sectors read
    @variable  r_time:int            Time spent reading, in ms
    @variable  w_complete:int        Writes completed
    @variable  w_merge:int           Writes merged
    @variable  w_sectors:int         Sectors written
    @variable  w_time:int            Time spent writing, in ms
    @variable  io_current:int        I/O:s currently in progress
    @variable  io_time:int           Time spent doing I/O:s, in ms
    @variable  io_weighted_time:int  Weighted time spent doing I/O:s, in ms
    '''
    
    
    def __init__(self, fields):
        '''
        Constructor
        
        @param  fields:list<str|int>  Fields from /proc/diskstats converted to proper data type
        '''
        (self.major, self.minor, self.device) = fields[0 : 3]
        (self.r_complete, self.r_merge, self.r_sectors, self.r_time) = fields[3 : 7]
        (self.w_complete, self.w_merge, self.w_sectors, self.w_time) = fields[7 : 11]
        (self.io_current, self.io_time, self.io_weighted_time) = fields[11 : 14]

