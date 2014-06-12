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


class CPUInfo: # TODO enable setting scaling
    '''
    Data from /proc/cpuinfo and /sys/devices/system/cpu
    
    @variable  cpus:list<dict<str, str>>  Information about each CPU
    '''
    
    
    BIOS_FREQUENCY_LIMIT = 'cpufreq/bios_limit'
    '''
    CPU frequency limit per BIOS, in kHz
    
    @mapping  int
    '''
    
    SCALING_GOVERNOR = 'cpufreq/scaling_governor'
    '''
    CPU frequency scaling governor
    
    @mapping  str
    '''
    
    CPU_TRANSITION_LATENCY = 'cpufreq/cpuinfo_transition_latency'
    '''
    CPU transition latency, in ns
    
    @mapping  int
    '''
    
    AVAILABLE_FREQUENCIES = 'cpufreq/scaling_available_frequencies'
    '''
    Available CPU scaling frequencies, in kHz
    
    @mapping  itr<int>
    '''
    
    SCALING_DRIVER = 'cpufreq/scaling_driver'
    '''
    CPU frequency scaling driver
    
    @mapping  str
    '''
    
    AVAILABLE_SCALING_GOVERNORS = 'cpufreq/scaling_available_governors'
    '''
    Available CPU frequency scaling governor
    
    @mapping  itr<str>
    '''
    
    CURRENT_FREQUENCY = 'cpufreq/cpuinfo_cur_freq'
    MINIMUM_FREQUENCY = 'cpufreq/cpuinfo_min_freq'
    MAXIMUM_FREQUENCY = 'cpufreq/cpuinfo_max_freq'
    CURRENT_SCALING_FREQUENCY = 'cpufreq/scaling_cur_freq'
    MINIMUM_SCALING_FREQUENCY = 'cpufreq/scaling_min_freq'
    MAXIMUM_SCALING_FREQUENCY = 'cpufreq/scaling_max_freq'
    # TODO more CPU info
    #'cpufreq/affected_cpus'
    #'cpufreq/related_cpus'
    #'cpufreq/scaling_setspeed'
    #cache/
    #power/
    #topology/
    #thermal_throttle
    #/sys/devices/system/cpu/cpufreq/
    #/sys/devices/system/cpu/cpuidle/
    #/sys/devices/system/cpu/power/
    
    
    
    def __init__(self):
        '''
        Constructor
        '''
        cpuinfo = None
        with open('/proc/cpuinfo', 'rb') as file:
            cpuinfo = file.read()
        cpuinfo = cpuinfo.decode('utf-8', 'replace').replace('\t', '')
        cpuinfo = filter(lambda cpu : not cpu == '', cpuinfo.split('\n\n'))
        
        def f(line):
            cols = line.split(': ')
            key, value = cols[0].replace('_', ' '), ': '.join(cols[1:])
            return (key, value)
        self.cpus = [dict(f(line) for line in cpu.split('\n') if ': ' in line) for cpu in cpuinfo]
    
    
    def __contains__(self, key):
        '''
        Get whether or not a key is available for any CPU
        
        @param   key:str  The key
        @return  :bool    The availability
        '''
        return any(map(key in self.cpus, self.cpus))
    
    
    def __getitem__(self, key):
        '''
        Look up a field from '/proc/cpuinfo' for each CPU
        
        @param   key:str      The key
        @return  :list<str?>  The value associated with the key for each CPU, `None` where missing
        '''
        return [cpu[key] if key in cpu else None for cpu in self.cpus]
    
    
    def get(self, cpu, data):
        '''
        Read a information from sysfs for a CPU
        
        @param   cpu:int   The index of the CPU
        @param   data:str  The file inside the CPU's directory
        @return  :str      The content of the file
        '''
        if data == CPUInfo.CURRENT_FREQUENCY:
            return str(int(float(self['cpu MHz'][cpu]) * 1000))
        path = '/sys/devices/system/cpu/cpu%i/%s' % (cpu, data)
        with open(path, 'rb') as file:
            cont = file.read().decode('utf-8', 'replace').rstrip('\n')
        return cont

