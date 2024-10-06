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
    @variable  keys:frozenset           List of all keys
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
        
        self.keys = self.__info.keys()
        
        self.mem_total = self['MemTotal']
        self.buffers = self['Buffers']
        self.cached = self['Cached']
        self.mem_free = self['MemFree'] + self.buffers + self.cached + self.get('KReclaimable', self.get('SReclaimable'))
        self.mem_used = self.mem_total - self.mem_free
        self.swap_cached = self['SwapCached']
        self.swap_total = self['SwapTotal']
        self.swap_free = self['SwapFree']
        self.swap_used = self.swap_total - (self.swap_free + self.swap_cached)
        self.shmem = self.get('Shmem', None)
        self.slab = self.get('Slab', None)
        self.hardware_corrupted = self.get('HardwareCorrupted', None)
    
    
    def __contains__(self, key):
        '''
        Get whether or not a key is available
        
        @param   key:str  The key
        @return  :bool    The availability
        '''
        return key in self.__info


    def get(self, key, default = 0):
        '''
        Look up a field from '/proc/meminfo'
        
        @param   key:str      The field name
        @param   default:int  The value to return if the field does not exist
        @return  :int         The value of the field, without the unit (KB if any)
        
        This keys should be available, but are most probably more available:
        
        @key  MemTotal           Total usable RAM (physical RAM minus a few reserved bit minus kernel binary code)
        @key  MemFree            Amount of unused usable physical RAM
        @key  MemAvailable       An estimate of how much memory is available for starting new applications, without swapping
        @key  Buffers            Relatively temporary storage for raw disc blocks
        @key  Cached             In-memory cache for files read from the disc (the pagecache).
                                 Does not include SwapCached.
        @key  SwapCached         Memory that once was swapped out, is swapped
                                 back in but still also is in the swapfile
        @key  Active             Memory that has been used more recently and
                                 usually not reclaimed unless absolutely necessary
        @key  Inactive           Memory which has been less recently used. It is
                                 more eligible to be reclaimed for other purposes
        @key  Active(anon)       [To be documented.]
        @key  Inactive(anon)     [To be documented.]
        @key  Active(file)       [To be documented.]
        @key  Inactive(file)     [To be documented.]
        @key  Unevictable        [To be documented.]
        @key  Mlocked            [To be documented.]
        @key  HighTotal          Total amount of highmem. Highmem is all memory above ~860MB of physical
                                 memory. Highmem areas are for use by user-space programs, or for the page
                                 cache. The kernel must use tricks to access this memory, making it slower
                                 to access than lowmem.
        @key  HighFree           Amount of free highmem
        @key  LowTotal           Total amount of lowmem. Lowmem is memory which can be used for everything
                                 that highmem can be used for, but it is also available for the kernel's use
                                 for its own data structures. Among many other things, it is where everything
                                 from Slab is allocated. Bad things happen when you're out of lowmem.
        @key  LowFree            Amount of free lowmem
        @key  MmapCopy           [To be documented.]
        @key  SwapTotal          Total amount of swap space available
        @key  SwapFree           Amount of unused swap space available
        @key  Dirty              Memory which is waiting to get written back to the disc
        @key  Writeback          Memory which is actively being written back to the disc
        @key  AnonPages          Non-file backed pages mapped into userspace page tables
        @key  Mapped             Files which have been mmaped, such as libraries
        @key  Shmem              Amount of memory consumed in tmpfs(5) filesystems
        @key  KReclaimable       Kernel allocations that the kernel will attempt to reclaim under memory
                                 pressure. Includes SReclaimable, and other direct allocations with a shrinker.
        @key  Slab               In-kernel data structures cache
        @key  SReclaimable       Part of Slab, that might be reclaimed, such as caches
        @key  SUnreclaim         Part of Slab, that cannot be reclaimed on memory pressure
        @key  KernelStack        Amount of memory allocated to kernel stacks
        @key  PageTables         Amount of memory dedicated to the lowest level of page tables
        @key  Quicklists         [To be documented.]
        @key  NFS_Unstable       NFS pages sent to the server, but not yet committed to stable storage
        @key  Bounce             Memory used for block device “bounce buffers”
        @key  WritebackTmp       Memory used by FUSE for temporary writeback buffers
        @key  CommitLimit        The total amount of memory currently available to be allocated
                                 on the system. Based on overcommit ratio.
        @key  Committed_AS       The amount of memory presently allocated on the system.
        @key  VmallocTotal       Total size of vmalloc memory area
        @key  VmallocUsed        Amount of vmalloc area which is used
        @key  VmallocChunk       Largest contiguous block of vmalloc area which is free
        @key  Percpu             [To be documented.]
        @key  HardwareCorrupted  [To be documented.]
        @key  LazyFree           Shows the amount of memory marked by madvise(2) MADV_FREE
        @key  AnonHugePages      Non-file backed huge pages mapped into userspace page tables
        @key  ShmemHugePages     Memory used by shared memory (shmem) and tmpfs(5) allocated with huge pages
        @key  ShmemPmdMapped     Shared memory mapped into user space with huge pages
        @key  CmaTotal           Total CMA (Contiguous Memory Allocator) pages
        @key  CmaFree            Free CMA (Contiguous Memory Allocator) pages
        @key  HugePages_Total    The size of the pool of huge pages
        @key  HugePages_Free     The number of huge pages in the pool that are not yet allocated
        @key  HugePages_Rsvd     This is the number of huge pages for which a commitment to allocate from
                                 the pool has been made, but no allocation has yet been made. These reserved
                                 huge pages guarantee that an application will be able to allocate a huge
                                 page from the pool of huge pages at fault time
        @key  HugePages_Surp     This is the number of huge pages in the pool above the value in
                                 /proc/sys/vm/nr_hugepages. The maximum number of surplus huge pages is
                                 controlled by /proc/sys/vm/nr_overcommit_hugepages.
        @key  Hugepagesize       The size of huge pages
        @key  Hugetlb            [To be documented.]
        @key  DirectMap4k        Number of bytes of RAM linearly mapped by kernel in 4kB pages
        @key  DirectMap2M        Number of bytes of RAM linearly mapped by kernel in 2MB pages
        @key  DirectMap4M        Number of bytes of RAM linearly mapped by kernel in 4MB pages
        @key  DirectMap1G        Number of bytes of RAM linearly mapped by kernel in 1GB pages
        '''
        return self.__info.get(key, default)


    def __getitem__(self, key):
        '''
        Equivalent to `self.get(key)`, except
        it fails rather than return 0 if the
        field does not exist
        '''
        return self.__info[key]
