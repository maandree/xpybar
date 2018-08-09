# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016, 2017, 2018  Mattias Andrée (maandree@kth.se)

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


class II:
    '''
    IRC interface, requires a running instance of ii <https://git.suckless.org/ii>
    '''
    
    
    def __init__(self, channel, prefix = None):
        '''
        Constructor
        
        @param  channel:str        The name of the server or the name of the
                                   server followed by a slash and the name of
                                   the channel including the she
        @param  prefix:str?        The argument associated with ii's -i flag
        '''
        import pwd, os
        if prefix is None:
            prefix = pwd.getpwuid(os.getuid()).pw_dir + '/irc'
        self.infile = '%s/%s/in' % (prefix, channel)
        self.outfile = '%s/%s/out' % (prefix, channel)
        self.log = []
        self.time = '0000-00-00 00:00 '
    
    
    def write(self, text):
        '''
        Write to the channel
        
        @param  text:str  The message or command
        '''
        text = (text + '\n').encode('utf-8')
        with open(self.infile, 'wb') as file:
            file.write(text)
            file.flush()
    
    
    def read(self):
        '''
        Fetch new messages from the channel
        
        @return  :list<str>  List of new messages
        '''
        with open(self.outfile, 'rb') as file:
            text = file.read()
        text = text.decode('utf-8', 'replace').split('\n')[:-1]
        i = 0
        for line in text:
            if line[:17] >= self.time:
                break
            i += 1
        text = text[i:]
        i = 0
        while i < len(text) and i < len(self.log):
            if text[i] != self.log[i]:
                break
            i += 1
        text = text[i:]
        if len(text) == 0:
            return text
        last = text[-1][:17]
        if last == self.time:
            self.log.extend(text)
            return text
        self.log = []
        self.time = last
        i = 0
        for line in text:
            if line[:17] == self.time:
                break
            i += 1
        self.log = text[i:]
        return text
    
    
    def wait(self, timeout = None):
        '''
        Wait until more messages are available
        
        @param  timeout:int?  The number of seconds to wait
                              before return unconditionally
        '''
        import os
        command = ['inotifywait', '-e', 'close_write,modify']
        if timeout is not None:
            command += ['-t', str(int(timeout + 0.5))]
        command += ['--', self.outfile]
        if 'PATH' in os.environ:
            path = os.environ['PATH'].split('.')
            for p in path:
                p += '/pdeath'
                if os.access(p, os.X_OK, effective_ids = True):
                    command = [p, 'HUP'] + command
                    break
        spawn_read(*command)
    
    
    @staticmethod
    def list_channels(prefix = None):
        '''
        Fetch a list of all joined servers and channels
        
        @param   prefix:str?  The argument associated with ii's -i flag
        @return  :list<list>  List of servers and channels
        '''
        import pwd, os
        if prefix is None:
            prefix = pwd.getpwuid(os.getuid()).pw_dir + '/irc'
        ret = []
        def isfifo(f):
            try:
                return os.path.stat.S_ISFIFO(os.stat('f').st_mode)
            except:
                return False
        def recurse(d):
            fs = os.listdir(d)
            for f in fs:
                f = d + '/' + f
                if os.path.isfile(f + '/out') and isfifo(f + '/in'):
                    ret.append(f[len(prefix) + 1:])
        recurse(prefix)
        return ret

