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

import os

from util import *

from plugins.linereader import LineReader



class Ping:
    '''
    Network connectivity monitor using ICMP echos
    
    @variable  monitors:dict<str, list<Ping.create_monitor.PingMonitor>>
                   Map from network interface to list of network monitors
                   connected against the server specified by the corresponding
                   element in `targets` of `__init__`
    '''
    
    DEFAULT_GATEWAY = ...
    '''
    Selects the default gateway's IP address
    '''
    
    UNITS = { 'ns' : 0.000001, 'us' : 0.001, 'µs' : 0.001, 'ms' : 1.0, 's' : 1000.0 }
    
    
    def __init__(self, targets = None, interval = 5, arguments = None, buffer_size = 8):
        '''
        Constructor
        
        @param  targets:dict<str, itr<str|...>>  Map from network interfaces to servers to ping
        @param  interval:float                   The pinging interval, in seconds
        @param  arguments:itr<str>?              Extra arguments for the `ping` command
        '''
        if targets is None:
            targets = Ping.get_nics()
        gateways = Ping.get_default_gateways()
        args = ['ping', '-i', str(interval)] + (arguments if arguments is not None else [])
        def get(nic, target):
            if target == Ping.DEFAULT_GATEWAY:
                target = None if nic not in gateways else gateways[nic]
            if target is None:
                return None
            command = args + ['-I', nic, target]
            return Ping.create_monitor(command, buffer_size, interval)
        self.monitors = dict((nic, [get(nic, t) for t in targets[nic]]) for nic in targets.keys())
    
    
    @staticmethod
    def get_nics(server = ...):
        '''
        List all network interfaces with a default gateway
        and map them to `server`
        
        @return  :dict<str, [`server`]>  Dictionary of network interfaces mapped to `server`
        '''
        data = spawn_read('ip', 'route').split('\n')
        def get(fields):
            device = fields[fields.index('dev') + 1]
            return (device, [server])
        return dict(get(line.split(' ')) for line in data if line.startswith('default via '))
    
    
    @staticmethod
    def get_default_gateways():
        '''
        All network interfaces with a default gateway mapped to their default gateways
        
        @return  :dict<str, str>  Map from network interfaces to their default gateways
        '''
        data = spawn_read('ip', 'route').split('\n')
        def get(fields):
            gateway = fields[2]
            device = fields[fields.index('dev') + 1]
            return (device, gateway)
        return dict(get(line.split(' ')) for line in data if line.startswith('default via '))
    
    
    @staticmethod
    def create_monitor(command, buffer_size, interval):
        import time
        class PingMonitor:
            def __init__(self):
                self.latency_buffer = [None] * buffer_size
                self.semaphore = threading.Semaphore()
                self.last_read = time.monotonic()
                self.last_icmp_seq = 0
            
            def start(self):
                with LineReader(spawn(*command)) as reader:
                    reader.next()
                    while True:
                        line = reader.next()
                        self.semaphore.acquire()
                        try:
                            line = line.replace('=', ' ').split(' ')
                            icmp_seq = int(line[line.index('icmp_seq') + 1])
                            ping_time = float(line[line.index('time') + 1])
                            ping_time *= Ping.UNITS[line[line.index('time') + 2]]
                            dropped_pkgs = icmp_seq - self.last_icmp_seq - 1
                            dropped_pkgs = [None] * dropped_pkgs
                            self.last_icmp_seq = icmp_seq
                            self.latency_buffer[:] = ([ping_time] + dropped_pkgs + self.latency_buffer)[:buffer_size]
                            self.last_read = time.monotonic()
                        except:
                            pass
                        finally:
                            self.semaphore.release()
            
            
            def get_latency(self, acquired = False):
                '''
                Get the average responses-time
                
                @return  :list<float?>  For index `n` (limited to `buffer_size` inclusively):
                                        the average response time for the latest `n - d` received
                                        pongs, where `d` is not number of dropped packages of the
                                        latest `n` sent pings. If the average response time cannot
                                        be calculated (if all packages have been dropped), the
                                        value will be `None`. Note that the value at index 0 will
                                        always be `None`, because index 0 means no packages.
                '''
                if not acquired:
                    self.semaphore.acquire()
                try:
                    rc = [None]
                    cursum = 0
                    samples = 0
                    for i in range(buffer_size):
                        if self.latency_buffer[i] is not None:
                            cursum += self.latency_buffer[i]
                            samples += 1
                        rc.append(None if samples == 0 else cursum / samples)
                    return rc
                finally:
                    if not acquired:
                        self.semaphore.release()
            
            def dropped(self, acquired = False):
                '''
                Estimate how many echos have been dropped since the last pong
                
                @return  :int  The estimated number of dropped packages
                '''
                if not acquired:
                    self.semaphore.acquire()
                try:
                    return (time.monotonic() - self.last_read) // interval
                finally:
                    if not acquired:
                        self.semaphore.release()
            
            def dropped_time(self, acquired = False):
                '''
                Estimate for how long packages have been dropping
                
                @return  :float  The estimated time packages have been dropping, in seconds
                '''
                if not acquired:
                    self.semaphore.acquire()
                try:
                    time_diff = time.monotonic() - self.last_read
                    return 0 if time_diff < interval else time_diff
                finally:
                    if not acquired:
                        self.semaphore.release()
        
        monitor = PingMonitor()
        xasync(monitor.start)
        return monitor

