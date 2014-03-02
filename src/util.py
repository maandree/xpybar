#!/usr/bin/env python3
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
import sys
import time
import threading
import subprocess

import Xlib.threaded


def async(target, name = None, group = None):
    '''
    Start a function asynchronously
    
    @param   target:()→void  The function
    @param   name:str?       The name of the thread
    @return  :Thread         A running deamon-thread running `target`, with the name `name`
    '''
    t = threading.Thread(target = target, name = name)
    t.setDaemon(True)
    t.start()
    return t


def watch(interval, target, delay = 0):
    '''
    Run a function periodically forever
    
    @param  interval:float  The number of seconds to sleep between invocatons
    @param  target:()→void  The function
    @param  delay:float     Number of extra seconds seconds to wait the first time
    '''
    target()
    if not delay == 0:
        time.sleep(delay)
    while True:
        time.sleep(interval)
        target()


def spawn(*command):
    '''
    Spawn an external process
    
    @param   command:*str  The command line
    @return  :istream      The process's stdout
    '''
    proc = subprocess.Popen(list(command), stderr = sys.stderr, stdout = subprocess.PIPE)
    return proc.stdout


def spawn_read(*command):
    '''
    Spawn an external process and returns its output
    
    @param   command:*str  The command line
    @return  :str          The process's output to stdout, without the final LF
    '''
    proc = subprocess.Popen(list(command), stderr = sys.stderr, stdout = subprocess.PIPE)
    out = proc.stdout.read().decode('utf-8', 'replace')
    if out.endswith('\n'):
        out = out[:-1]
    return out
