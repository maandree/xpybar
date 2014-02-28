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


class AverageLoad:
    '''
    The current average load, number of scheduling entities and latest PID
    
    @variable  avg_5_min:float   The average load over the last 5 minutes
    @variable  avg_10_min:float  The average load over the last 10 minutes
    @variable  avg_15_min:float  The average load over the last 15 minutes
    @variable  active_tasks:int  The number of active scheduling entities
    @variable  total_tasks:int   The total number of scheduling entities
    @variable  last_pid:int      The PID of the last created process on the system
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
        
        self.avg_5_min, self.avg_10_min, self.avg_15_min, tasks, self.last_pid = uptime[:5]
        self.avg_5_min = float(self.avg_5_min)
        self.avg_10_min = float(self.avg_10_min)
        self.avg_15_min = float(self.avg_15_min)
        self.last_pid = int(self.last_pid)
        self.active_tasks, self.total_tasks = [int(t) for t in tasks.split('/')]

