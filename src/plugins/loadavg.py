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


class AverageLoad:
    '''
    The current average load, number of scheduling entities and latest PID
    
    @variable  total_avg_5_min:float     The average load over the last 5 minutes, sum of processors
    @variable  total_avg_10_min:float    The average load over the last 10 minutes, sum of processors
    @variable  total_avg_15_min:float    The average load over the last 15 minutes, sum of processors
    @variable  average_avg_5_min:float   The average load over the last 5 minutes, average of processors
    @variable  average_avg_10_min:float  The average load over the last 10 minutes, average of processors
    @variable  average_avg_15_min:float  The average load over the last 15 minutes, average of processors
    @variable  active_tasks:int          The number of active scheduling entities
    @variable  total_tasks:int           The total number of scheduling entities
    @variable  last_pid:int              The PID of the last created process on the system
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
        with open('/proc/loadavg', 'rb') as file:
            uptime = file.read()
        uptime = uptime.decode('utf-8', 'replace')
        uptime = uptime.replace('\n', ' ').split(' ')
        
        if AverageLoad.cpu_count is None:
            with open('/proc/cpuinfo', 'rb') as file:
                AverageLoad.cpu_count = file.read()
            AverageLoad.cpu_count = AverageLoad.cpu_count.decode('utf-8', 'replace').split('\n')
            AverageLoad.cpu_count = filter(lambda line : 'processor' in line, AverageLoad.cpu_count)
            AverageLoad.cpu_count = len(list(AverageLoad.cpu_count))
        
        self.total_avg_5_min, self.total_avg_10_min, self.total_avg_15_min, tasks, self.last_pid = uptime[:5]
        self.total_avg_5_min = float(self.total_avg_5_min)
        self.total_avg_10_min = float(self.total_avg_10_min)
        self.total_avg_15_min = float(self.total_avg_15_min)
        self.average_avg_5_min = self.total_avg_5_min / AverageLoad.cpu_count
        self.average_avg_10_min = self.total_avg_10_min / AverageLoad.cpu_count
        self.average_avg_15_min = self.total_avg_15_min / AverageLoad.cpu_count
        self.last_pid = int(self.last_pid)
        self.active_tasks, self.total_tasks = [int(t) for t in tasks.split('/')]

