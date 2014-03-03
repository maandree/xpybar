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


def reduce(f, items):
    '''
    https://en.wikipedia.org/wiki/Fold_(higher-order_function)
    
    @param   f:(¿E?, ¿E?)→¿E?  The function
    @param   item:itr<¿E?>     The input
    @return  ¿E?               The output
    '''
    if len(items) < 2:
        return items
    rc = items[0]
    for i in range(1, len(items)):
        rc = f(rc, items[i])
    return rc


class Sometimes:
    '''
    Function wrapper for only actually invoking
    the function every n:th time, where n is a
    customisable parameter
    '''
    
    def __init__(self, function, interval, initial = 0):
        '''
        Constructor
        
        @param  function:(*?)→¿R?  The function
        @param  interval:int       Invoke the function every `interval`:th time
        @param  initial:int        The of times needed to invoke before actual invocation
        '''
        self.function = function
        self.interval = interval
        self.counter = initial
    
    def __call__(self, *args, **kargs):
        '''
        Invoke the function, every `interval`:th time
        
        @param   args:*?    The parameters of the function
        @param   kargs:**?  The named parameters of the function
        @return  :¿R??      The return value of the function, `None` if not invoked
        '''
        rc = None
        if self.counter == 0:
            rc = self.function(*args, **kargs)
            self.counter = self.interval
        self.counter -= 1
        return rc

