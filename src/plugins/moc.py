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

import sys
import subprocess

from util import *


class MOC: # TODO add support for waiting for events and reading settings
    '''
    Music On Console interface
    
    @variable  state  The state of moc, one of: MOC.NOT_RUNNING,
                      MOC.STOPPED, MOC.PAUSED, MOC.PLAYING
    '''
    
    
    NOT_RUNNING = None
    '''
    The MOC server is not running
    '''
    
    STOPPED = 'STOP'
    '''
    No file is played
    '''
    
    PAUSED = 'PAUSE'
    '''
    The current file is paused
    '''
    
    PLAYING = 'PLAY'
    '''
    The current file is playing
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        self.__info = {}
        for line in MOC.__interact('--info').stdout.read().decode('utf-8', 'replace').split('\n'):
            if ': ' in line:
                line = line.split(': ')
                self.__info[line[0]] = ': '.join(line[1:])
        self.state = self['State'] if 'State' in self else None
    
    
    def __contains__(self, key):
        '''
        Get whether or not a key is available
        
        @param   key:str  The key
        @return  :bool    The availability
        '''
        return key in self.__info
    
    
    def __getitem__(self, key):
        '''
        Get a details
        
        @param   key:str  The key
        @return  :str     The value associated with the key
        
        The following are defined (may be empty) if moc is
        playing or paused: File, Title, Artist, SongTitle,
        Album, TotalTime, TimeLet, TotalSec, CurrentTime,
        CurrentSec, Bitrate.
        '''
        return self.__info[key]
    
    
    def keys(self):
        '''
        Get available detail keys
        
        @return  :itr<str>  The keys
        '''
        return self.__info.keys()
    
    
    @staticmethod
    def __interact(*args):
        '''
        Run mocp
        
        @param   args:*str  The command line arguments, except the first
        @return  :Popen     The spawned process
        '''
        command = ['mocp'] + list(args)
        return subprocess.Popen(command, stderr = subprocess.PIPE, stdout = subprocess.PIPE)
    
    
    @staticmethod
    def enqueue(files):
        '''
        Add files to the queue
        
        @param   files:itr<str>  The files
        @return  :Popen          The spawned process
        '''
        return MOC.__interact('--enqueue', '--', *files)
    
    
    @staticmethod
    def append(files):
        '''
        Append files, directories (recursively) and playlists to the playlist
        
        @param   files:itr<str>  The files
        @return  :Popen          The spawned process
        '''
        return MOC.__interact('--append', '--', *files)
    
    
    @staticmethod
    def clear():
        '''
        Clear the playlist
        
        @return  :Popen  The spawned process
        '''
        return MOC.__interact('--clear')
    
    
    @staticmethod
    def play():
        '''
        Start playing from the first item on the playlist
        
        @return  :Popen  The spawned process
        '''
        return MOC.__interact('--play')
    
    
    @staticmethod
    def next():
        '''
        Request playing the next song from the server's playlist
        
        @return  :Popen  The spawned process
        '''
        return MOC.__interact('--next')
    
    
    @staticmethod
    def previous():
        '''
        Request playing the previous song from the server's playlist
        
        @return  :Popen  The spawned process
        '''
        return MOC.__interact('--previous')
    
    
    @staticmethod
    def stop():
        '''
        Request the server to stop playing
        
        @return  :Popen  The spawned process
        '''
        return MOC.__interact('--stop')
    
    
    @staticmethod
    def exit():
        '''
        Bring down the server
        
        @return  :Popen  The spawned process
        '''
        return MOC.__interact('--exit')
    
    
    @staticmethod
    def pause():
        '''
        Request the server to pause playing
        
        @return  :Popen  The spawned process
        '''
        return MOC.__interact('--pause')
    
    
    @staticmethod
    def unpause():
        '''
        Request the server to resume playing when paused
        
        @return  :Popen  The spawned process
        '''
        return MOC.__interact('--unpause')
    
    
    @staticmethod
    def toggle_pause():
        '''
        Toggle between play and pause
        
        @return  :Popen  The spawned process
        '''
        return MOC.__interact('--toggle-pause')
    
    
    @staticmethod
    def seek(seconds):
        '''
        Seek forward (positive) or backward (negative) in the file currently being played
        
        @param   seconds:int  The number of seconds to seek forward, negative for backwards
        @return  :Popen?      The spawned process, `None` if nothing is spawned
        '''
        if not seconds == 0:
            return MOC.__interact('--seek', ('+%i' if seconds > 0 else '%i') % (seconds))
        return None
    
    
    @staticmethod
    def volume(volume, relative = True):
        '''
        Adjust the mixer volume
        
        @param   volume:int     The volume or volume increment
        @param   relative:bool  Whether to adjust, otherwise set
        @return  :Popen         The spawned process
        '''
        if relative and (not volume == 0):
            return MOC.__interact('--volume', ('+%i' if volume > 0 else '%i') % (volume))
        return MOC.__interact('--volume', '%i' % (max(0, volume)))
    
    
    @staticmethod
    def jump(position, precents = False):
        '''
        Jump to some position in the current file
        
        @param   position:int   The position either in seconds or precents
        @param   precents:bool  Whether to use precents, otherwise seconds
        @return  :Popen         The spawned process
        '''
        return MOC.__interact('--jump', '%i%s' % (position, '%' if precents else 's'))
    
    
    def toggle(shuffle = False, repeat = False, autonext = False):
        '''
        Toggle options
        
        @param   shuffle:bool   Whether to toggle shuffle
        @param   repeat:bool    Whether to toggle repeat
        @param   autonext:bool  Whether to toggle autonext
        @return  :Popen?        The spawned process, `None` if nothing is spawned
        '''
        if any([shuffle, repeat, autonext]):
            opts = [('shuffle', shuffle), ('repeat', repeat), ('autonext', autonext)]
            opts = map(lambda opt_val : opt_val[0] if opt_val[1] else None, opts)
            opts = filter(lambda opt : opt is not None, opts)
            return MOC.__interact('--toggle', ','.join(opts))
        return None
    
    
    def on(shuffle = False, repeat = False, autonext = False):
        '''
        Turn on options
        
        @param   shuffle:bool   Whether to turn on shuffle
        @param   repeat:bool    Whether to turn on repeat
        @param   autonext:bool  Whether to turn on autonext
        @return  :Popen?        The spawned process, `None` if nothing is spawned
        '''
        if any([shuffle, repeat, autonext]):
            opts = [('shuffle', shuffle), ('repeat', repeat), ('autonext', autonext)]
            opts = map(lambda opt_val : opt_val[0] if opt_val[1] else None, opts)
            opts = filter(lambda opt : opt is not None, opts)
            return MOC.__interact('--on', ','.join(opts))
        return None
    
    
    def off(shuffle = False, repeat = False, autonext = False):
        '''
        Turn off options
        
        @param   shuffle:bool   Whether to turn off shuffle
        @param   repeat:bool    Whether to turn off repeat
        @param   autonext:bool  Whether to turn off autonext
        @return  :Popen?        The spawned process, `None` if nothing is spawned
        '''
        if any([shuffle, repeat, autonext]):
            opts = [('shuffle', shuffle), ('repeat', repeat), ('autonext', autonext)]
            opts = map(lambda opt_val : opt_val[0] if opt_val[1] else None, opts)
            opts = filter(lambda opt : opt is not None, opts)
            return MOC.__interact('--off', ','.join(opts))
        return None

