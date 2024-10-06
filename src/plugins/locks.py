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


class Locks:
    '''
    File lock statistics
    
    @variable  locks:list<Locks.Lock>  List of file-locks
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        def convert(fields):
            fields[0] = int(fields[0])
            fields[4] = int(fields[4])
            fields[5] = int(fields[5], 16)
            fields[6] = int(fields[6], 16)
            fields[7] = int(fields[7])
            fields[8] = int(fields[8])
            fields[9] = int(fields[9]) if not fields[9] == 'EOF' else None
            return fields
        with open('/proc/locks', 'rb') as file:
            data = file.read()
        data = data.decode('utf-8', 'replace').rstrip('\n').replace(':', ' ').replace('  ', ' ')
        while '  ' in data:
            data = data.replace('  ', ' ')
        self.locks = [Locks.Lock(*convert(line.split(' '))) for line in data.split('\n')]
    
    
    @staticmethod
    def find_device(major, minor):
        '''
        Find a device from its major and minor number
        
        This method will not work if a mount's mountpoint or a
        device's pathname includes spaces or line feeds.
        
        @param   major:int                                The major number of the device, in decimal form
        @param   minor:int                                The minor number of the device, in decimal form
        @return  (root:str, mountpoint:str, device:str)?  The root of the mount within the filesystem,
                                                          the mountpoint relative to the process's root,
                                                          and the mounted device (pathname or RAM filesystem),
                                                          `None` if not found
        '''
        with open('/proc/self/mountinfo', 'rb') as file:
            data = file.read()
        data = data.decode('utf-8', 'strict').rstrip('\n').split('\n')
        devnum = '%i:%i' % (major, minor)
        for line in data:
            line = line.split(' ')
            if not line[2] == devnum:
                continue
            return (line[3], line[4], line[-2])
        return None
    
    
    @staticmethod
    def find_pathname(mountpoint, inode, alarm = 1):
        '''
        Find the pathname of a file based on its mountpoint and inode number
        
        @param   mountpoint:str  The mountpoint of the file
        @param   inode:int       The inode number of the file
        @param   alarm:int|str?  The time limit of the search, `None` to search forever
        @return  :list<str>      All found pathnames of the file
        '''
        from subprocess import Popen, PIPE
        command = ['find', mountpoint, '-inum', str(inode), '-mount', '-print0']
        if alarm is not None:
            command = ['alarm', str(inode)] + command
        found = Popen(command, stdin = PIPE, stdout = PIPE, stderr = PIPE).communicate()[0]
        found = found.decode('utf-8', 'replace').rstrip('\n')
        found = [pathname for pathname in found.split('\0') if not pathname == '']
        return found
    
    
    @staticmethod
    def find(major, minor, inode, alarm = 1):
        '''
        Find the pathname of a file based on its device's major and minor number and its inode number
        
        @param   major:int       The major number of the device, in decimal form
        @param   minor:int       The minor number of the device, in decimal form
        @param   inode:int       The inode number of the file
        @param   alarm:int|str?  The time limit of the search, `None` to search forever
        @return  :list<str>      All found pathnames of the file
        '''
        device = Locks.find_device()
        if device is None:
            return []
        return Locks.find_pathname(device[1], inode, alarm)
    
    
    class Lock:
        '''
        Information about a file-lock
        
        @variable  lock_id:int     The unique ID of the lock
        @variable  lock_type:str   Either 'FLOCK' or 'POSIX', indicating what lock system has been used,
                                   'FLOCK' indicates the 'flock' system call, and 'POSIX' indicates the
                                   'lockf' system call.
        @variable  mandatory:bool  Whether the lock is mandatory rather than advisory
        @variable  shared:bool     Whether the process has locked the file for reading rather than writing
        @variable  pid:int         The ID of the process that has locked the file
        @variable  major:int       The major number of the device on which the locked file is stored
        @variable  minor:int       The minor number of the device on which the locked file is stored
        @variable  inode:int       The inode number of the locked file
        @variable  start:int       The index of the first bytes of the locked area
        @variable  end:int?        The index of the last bytes of the locked area, `None` for end-of-file
        '''
        def __init__(self, lock_id, lock_type, lock_level, sharedness, pid, major, minor, inode, start, end):
            '''
            Constructor
            
            @param  lock_id:int     The unique ID of the lock
            @param  lock_type:str   Either 'FLOCK' or 'POSIX', indicating what lock system has been used,
                                    'FLOCK' indicates the 'flock' system call, and 'POSIX' indicates the
                                    'lockf' system call.
            @param  lock_level:str  Either 'MANDATORY' or 'ADVISORY' indicating the level of the lock
            @param  sharedness:str  Either 'READ' or 'WRITE' indicating the sharedness of the lock
            @param  pid:int         The ID of the process that has locked the file
            @param  major:int       The major number of the device on which the locked file is stored
            @param  minor:int       The minor number of the device on which the locked file is stored
            @param  inode:int       The inode number of the locked file
            @param  start:int       The index of the first bytes of the locked area
            @param  end:int?        The index of the last bytes of the locked area, `None` for end-of-file
            '''
            self.lock_id    = lock_id
            self.lock_type  = lock_type
            self.mandatory  = lock_level == 'MANDATORY'
            self.shared     = sharedness == 'READ'
            self.pid        = pid
            self.major      = major
            self.minor      = minor
            self.inode      = inode
            self.start      = start
            self.end        = end
        
        
        def find_device(self):
            '''
            Find the device that the locked file is located on
            
            This method will not work if a mount's mountpoint or a
            device's pathname includes spaces or line feeds.
            
            @return  (root:str, mountpoint:str, device:str)?  The root of the mount within the filesystem,
                                                              the mountpoint relative to the process's root,
                                                              and the mounted device (pathname or RAM
                                                              filesystem), `None` if not found
            '''
            return Locks.find_device(self.major, self.minor)
        
        
        def find_pathname(self, mountpoint, alarm = 1):
            '''
            Find the pathname of the locked file based on its mountpoint
            
            @param   mountpoint:str  The mountpoint of the file
            @param   alarm:int|str?  The time limit of the search, `None` to search forever
            @return  :list<str>      All found pathnames of the file
            '''
            return Locks.find_pathname(mountpoint, self.inode, alarm)
        
        
        def find(self, alarm = 1):
            '''
            Find the pathname of the locked file
            
            @param   alarm:int|str?  The time limit of the search, `None` to search forever
            @return  :list<str>      All found pathnames of the file
            '''
            return Locks.find(self.major, self.minor, self.inode, alarm)

