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

import os

from util import *

from plugins.linereader import LineReader



class Inotify:
    '''
    File access monitor
    '''
    
    def __init__(self, callback, *arguments, events = None):
        '''
        Constructor
        
        @param  callback:(str)→void  Function that will be called everytime a line is read from
                                     `inotifywait`'s standard output, the parameter will be that line,
                                     note that this will not be asynchronously, you may want to specify
                                     something like `lambda : async(fun)` for that, and use semaphores
                                     in `fun`.
        @param  arguments:*str       The files and directories you want to watch and any addition
                                     argument you want to pass to `inotifywait`
        @param  event:itr<str>?      Event you want reported, see "EVENTS" under `inotifywait`'s man page
        '''
        command = ['inotifywait', '-m']
        if events is not None:
            if isinstance(events, str):
                events = [events]
            for event in events:
                command.append('-e')
                command.append(event)
        command += list(arguments)
        def start():
            with LineReader(spawn(*command)) as reader:
                while True:
                    callback(reader.next())
        async(start)
