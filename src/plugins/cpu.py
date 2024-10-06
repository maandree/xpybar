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


class CPU:
    '''
    Retrieve processor statistics
    
    @variable  cpu:list<int>                Accumulative processors statistics
    @variable  cpus:list<list<int>>         Individual processors statistics
    @variable  intr:list<int>               Counts of individual interrupts serviced since boot time
    @variable  intr_total:int               Sum of `intr`
    @variable  ctxt:int                     The number of context switches that the system underwent.
    @variable  btime:int                    Boot time, in seconds since the Epoch, 1970-01-01 00:00:00 UTC
    @variable  processes:int                Number of forks and clones (and similar) created since boot
    @variable  procs_running:int?           Number of processes in runnable state (linux>=2.5.45)
    @variable  procs_blocked:int?           Number of processes blocked waiting for I/O to complete (linux>=2.5.45)
    @variable  softirq:list<int>?           Counts of individual software IRQ since boot time
    @variable  softirq_total:int?           Sum of `softirq`
    @variable  fields:dict<str, list<int>>  Table with all information
    '''
    
    
    # These constants are index in the CPU statistcs, use for example `CPU_instance.cpu[CPU.user]`
    
    user = 0
    '''
    :int  Time spent in user mode, in USER_HZ (normally 1/100ths of a second, it is a time not a frequency)
    '''
    
    nice = 1
    '''
    :int  Time spent in user mode with low priority, in USER_HZ
    '''
    
    system = 2
    '''
    :int  Time spent in system mode, in USER_HZ
    '''
    
    idle = 3
    '''
    :int  Time spent in the idle task, in USER_HZ
    '''
    
    iowait = 4
    '''
    :int  Time waiting for I/O to complete, in USER_HZ (linux>=2.5.41)
    '''
    
    irq = 5
    '''
    :int  Time servicing interrupts, in USER_HZ (linux>=2.6.0-test4)
    '''
    
    softirq = 6
    '''
    :int  Time servicing softirqs, in USER_HZ (linux>=2.6.0-test4)
    '''
    
    steal = 7
    '''
    :int  Stolen time, which is the time spent in other operating systems
          when running in a virtualized environment, in USER_HZ (linux>=2.6.11)
    '''
    
    guest = 8
    '''
    :int  Time spent running a virtual CPU for guest operating systems
          under the control of the Linux kernel, in USER_HZ (linux>=2.6.24)
    '''
    
    guest_nice = 9
    '''
    :int  Time spent running a niced guest, in USER_HZ (linux>=2.6.33).
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        stat = None
        with open('/proc/stat', 'rb') as file:
            stat = file.read()
        stat = stat.decode('utf-8', 'replace')
        stat = filter(lambda x : not x == '', stat.split('\n'))
        
        fields = {}
        for line in stat:
            line = list(filter(lambda x : not x == '', line.split(' ')))
            fields[line[0]] = [int(x) for x in line[1:]]
        
        self.cpu = fields['cpu']
        i = 0
        self.cpus = []
        while ('cpu%i' % i) in fields:
            self.cpus.append(fields['cpu%i' % i])
            i += 1
        self.ctxt = fields['ctxt'][0]
        self.btime = fields['btime'][0]
        self.processes = fields['processes'][0]
        self.procs_running = fields['procs_running'][0] if 'procs_running' in fields else None
        self.procs_blocked = fields['procs_blocked'][0] if 'procs_blocked' in fields else None
        self.intr = fields['intr'][1:]
        self.intr_total = fields['intr'][0]
        self.softirq = fields['softirq'][1:] if 'softirq' in fields else None
        self.softirq_total = fields['softirq'][0] if 'softirq' in fields else None
        self.fields = fields

