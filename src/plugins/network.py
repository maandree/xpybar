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


class Network:
    '''
    Retrieve network statistics
    
    @variable  devices:dict<str, dict<str, int>>  Map from device name, to data name, to data value
    
    Data names for receive:
    
    @key  rx_bytes       Bytes received
    @key  rx_packets     Packets received
    @key  rx_errs        Errors
    @key  rx_drop        Dropped
    @key  rx_fifo        FIFO
    @key  rx_frame       Frame
    @key  rx_compressed  Compressed
    @key  rx_multicast   Multicast
    
    Data names for transmit:
    
    @key  tx_bytes       Bytes transmitted
    @key  tx_packets     Packets transmitted
    @key  tx_errs        Errors
    @key  tx_drop        Dropped
    @key  tx_fifo        FIFO
    @key  tx_colls       Collisions
    @key  tx_carrier     Carrier
    @key  tx_compressed  Compressed
    '''
    
    
    def __init__(self, *exclude):
        '''
        Constructor
        
        @param  exclude:*str  Devices to exclude
        '''
        stat = None
        with open('/proc/net/dev', 'rb') as file:
            stat = file.read()
        stat = stat.decode('utf-8', 'replace')
        stat = stat.replace('|', ' | ').replace(':', ' ')
        stat = list(filter(lambda x : not x == '', stat.split('\n')[1:]))
        stat = [list(filter(lambda x : not x == '', line.split(' '))) for line in stat]
        stat[0] = stat[0][2:]
        
        exclude = set(exclude)
        devices = {}
        for line in stat[1:]:
            if line[0] not in exclude:
                devices[line[0]] = [int(x) for x in line[1:]]
        
        columns, prefix = [], 'rx_'
        for column in stat[0]:
            if column == '|':
                prefix = 'tx_'
            else:
                columns.append(prefix + column)
        
        self.devices = {}
        for dev in devices.keys():
            fields = {}
            self.devices[dev] = fields
            values = devices[dev]
            for i in range(len(values)):
                fields[columns[i]] = values[i]

