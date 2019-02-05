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


class Uptime:
    '''
    The current uptime of the machine and how long it has been idle
    
    @variable  uptime_seconds:float                                            Total uptime
    @variable  total_idle_seconds:float                                        Total processor idle time
    @variable  average_idle_seconds:float                                      Average processor idle time
    @variable  uptime:(days:int, hours:int, minutes:int, seconds:float)        Total uptime
    @variable  total_idle:(days:int, hours:int, minutes:int, seconds:float)    Total processor idle time
    @variable  average_idle:(days:int, hours:int, minutes:int, seconds:float)  Average processor idle time
    '''
    
    cpu_count = None
    '''
    :int?  The number of processors on the machine
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        uptime = None
        with open('/proc/uptime', 'rb') as file:
            uptime = file.read()
        uptime = uptime.decode('utf-8', 'replace')
        uptime = uptime.replace('\n', ' ').split(' ')
        uptime, idle = float(uptime[0]), float(uptime[1])
        
        if Uptime.cpu_count is None:
            with open('/proc/cpuinfo', 'rb') as file:
                Uptime.cpu_count = file.read()
            Uptime.cpu_count = Uptime.cpu_count.decode('utf-8', 'replace').split('\n')
            Uptime.cpu_count = filter(lambda line : 'processor' in line, Uptime.cpu_count)
            Uptime.cpu_count = len(list(Uptime.cpu_count))
        
        self.uptime_seconds = uptime
        self.total_idle_seconds = idle
        self.average_idle_seconds = idle / Uptime.cpu_count
        
        self.uptime = Uptime.split_time(self.uptime_seconds)
        self.total_idle = Uptime.split_time(self.total_idle_seconds)
        self.average_idle = Uptime.split_time(self.average_idle_seconds)
    
    
    @staticmethod
    def split_time(t):
        '''
        Split a large number of seconds to days, hours, minutes and seconds
        
        @param   t:float  The number of seconds
        @return  :(days:int, hours:int, minutes:int, seconds:float)
                     The time split into days, hours [0, 23], minutes [0, 59] and seconds [0, 60[
        '''
        seconds, t = t % 60, t // 60
        minutes, t = int(t % 60), t // 60
        hours, t = int(t % 24), t // 24
        days = int(t)
        return (days, hours, minutes, seconds)

