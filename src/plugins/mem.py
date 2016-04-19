# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016  Mattias Andrée (maandree@member.fsf.org)

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


class Memory:
    '''
    Retrieve memory information
    
    @variable  mem_total:int            Total usable RAM (physical RAM minus a few reserved bit, in KB
                                        minus kernel binary code), in KB
    @variable  mem_free:int             Amount of unused usable physical RAM, in KB
    @variable  mem_used:int             Amount of used usable physical RAM, in KB
    @variable  buffers:int              Relatively temporary storage for raw disc blocks, in KB
    @variable  cached:int               In-memory cache for files read from the disc (the pagecache), in KB.
                                        Does not include swap_cached.
    @variable  swap_cached:int          Memory that once was swapped out, is swapped back in but still
                                        also is in the swapfile, in KB
    @variable  swap_total:int           Total amount of swap space available, in KB
    @variable  swap_free:int            Amount of unused swap space available, in KB
    @variable  swap_used:int            Memory which has been evicted from RAM to swap space, in KB
    @variable  shmem:int?               Amount of memory allocated as shared memory, in KB
    @variable  slab:int?                In-kernel data structures cache, in KB
    @variable  hardware_corrupted:int?  Hardware corrupted memory, in KB
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        meminfo = None
        with open('/proc/meminfo', 'rb') as file:
            meminfo = file.read()
        meminfo = meminfo.decode('utf-8', 'replace')
        meminfo = filter(lambda x : not x == '', meminfo.split('\n'))
        
        self.__info = {}
        for line in meminfo:
            line = filter(lambda x : not x == '', line.replace(':', ' ').split(' '))
            line = list(line)[:2]
            self.__info[line[0]] = int(line[1])
        
        self.mem_total = self['MemTotal']
        self.mem_free = self['MemFree']
        self.buffers = self['Buffers']
        self.cached = self['Cached']
        self.mem_used = self.mem_total - (self.mem_free + self.buffers + self.cached)
        self.swap_cached = self['SwapCached']
        self.swap_total = self['SwapTotal']
        self.swap_free = self['SwapFree']
        self.swap_used = self.swap_total - (self.swap_free + self.swap_cached)
        self.shmem = self['Shmem'] if 'Shmem' in self else None
        self.slab = self['Slab'] if 'Slab' in self else None
        self.hardware_corrupted = self['HardwareCorrupted'] if 'HardwareCorrupted' in self else None
    
    
    def __contains__(self, key):
        '''
        Get whether or not a key is available
        
        @param   key:str  The key
        @return  :bool    The availability
        '''
        return key in self.__info
    
    
    def __getitem__(self, key):
        '''
        Look up a field from '/proc/meminfo'
        
        @param   key:str  The field name
        @return  :int     The value of the field, without the unit (KB if any)
        
        This keys should be available, but are most probably more available:
        
        @key  MemTotal       Total usable RAM (physical RAM minus a few reserved bit minus kernel binary code)
        @key  MemFree        Amount of unused usable physical RAM
        @key  Buffers        Relatively temporary storage for raw disc blocks
        @key  Cached         In-memory cache for files read from the disc (the pagecache).
                             Does not include SwapCached.
        @key  SwapCached     Memory that once was swapped out, is swapped
                             back in but still also is in the swapfile
        @key  Active         Memory that has been used more recently and
                             usually not reclaimed unless absolutely necessary
        @key  Inactive       Memory which has been less recently used. It is
                             more eligible to be reclaimed for other purposes
        @key  SwapTotal      Total amount of swap space available
        @key  SwapFree       Amount of unused swap space available
        @key  Dirty          Memory which is waiting to get written back to the disc
        @key  Writeback      Memory which is actively being written back to the disc
        @key  AnonPages      Non-file backed pages mapped into userspace page tables
        @key  Mapped         Files which have been mmaped, such as libraries
        @key  Slab           In-kernel data structures cache
        @key  SReclaimable   Part of Slab, that might be reclaimed, such as caches
        @key  SUnreclaim     Part of Slab, that cannot be reclaimed on memory pressure
        @key  PageTables     Amount of memory dedicated to the lowest level of page tables
        @key  NFS_Unstable   NFS pages sent to the server, but not yet committed to stable storage
        @key  Bounce         Memory used for block device “bounce buffers”
        @key  WritebackTmp   Memory used by FUSE for temporary writeback buffers
        @key  CommitLimit    The total amount of memory currently available to be allocated
                             on the system. Based on overcommit ratio.
        @key  Committed_AS   The amount of memory presently allocated on the system.
        @key  VmallocTotal   Total size of vmalloc memory area
        @key  VmallocUsed    Amount of vmalloc area which is used
        @key  VmallocChunk   Largest contiguous block of vmalloc area which is free
        @key  AnonHugePages  Non-file backed huge pages mapped into userspace page tables
        '''
        return self.__info[key]

