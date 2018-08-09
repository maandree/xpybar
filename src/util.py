#!/usr/bin/env python3
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
import sys
import time
import threading
import subprocess


def setproctitle(title):
    '''
    Set process title
    
    @param  title:str  The title of the process
    '''
    import ctypes
    try:
        # Remove path, keep only the file,
        # otherwise we get really bad effects, namely
        # the name title is truncates by the number
        # of slashes in the title. At least that is
        # the observed behaviour when using procps-ng.
        title = title.split('/')[-1]
        # Create string buffer with title
        title = title.encode(sys.getdefaultencoding(), 'replace')
        title = ctypes.create_string_buffer(title)
        if 'linux' in sys.platform:
            # Set process title on Linux
            libc = ctypes.cdll.LoadLibrary('libc.so.6')
            libc.prctl(15, ctypes.byref(title), 0, 0, 0)
        elif 'bsd' in sys.platform:
            # Set process title on at least FreeBSD
            libc = ctypes.cdll.LoadLibrary('libc.so.7')
            libc.setproctitle(ctypes.create_string_buffer(b'-%s'), title)
    except:
        pass


def xasync(target, name = None, group = None):
    '''
    Start a function asynchronously
    
    @param   target:()→void  The function
    @param   name:str?       The name of the thread
    @return  :Thread         A running deamon-thread running `target`, with the name `name`
    '''
    def target_wrapper():
        if 'linux' in sys.platform: ## XXX I only know that will happen on Linux
            setproctitle(name)
        target()
    t = threading.Thread(target = target_wrapper if name is not None else target, name = name)
    t.setDaemon(True)
    t.start()
    return t
globals()['async'] = xasync ## xasync was named async until the release of Python 3.7 when it became a reserved keyword


def watch(interval, target, delay = 0):
    '''
    Run a function periodically forever
    
    @param  interval:float  The number of seconds to sleep between invocatons
    @param  target:()→void  The function
    @param  delay:float     Number of extra seconds to wait the first time
    '''
    if not delay == 0:
        time.sleep(delay)
    while True:
        target()
        time.sleep(interval)


def forever(target, delay = 0):
    '''
    Run a function continuously forever
    
    @param  target:()→void  The function
    @param  delay:float     Number of extra seconds to wait the first time
    '''
    if not delay == 0:
        time.sleep(delay)
    while True:
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
    @return  ¿E??              The output, `None` if `item` is empty
    '''
    if len(items) == 0:
        return None
    rc = items[0]
    for i in range(1, len(items)):
        rc = f(rc, items[i])
    return rc


def colour_aware_len(string, original_len = len):
    '''
    Colour-aware object length measurement function
    
    It is suggested to redefine `len` with this
    function in the following way.
    
        len_ = len
        len = lambda string : colour_aware_len(string, len_)
    
    @param   string:object              The object to measure
    @param   original_len:(object)→int  The original implementation of `len`
    @return  :int                       The length of `string`
    '''
    if not isinstance(string, str):
        return original_len(string)
    rc, esc = 0, False
    for c in string:
        if esc:
            if c == 'm':
                esc = False
        elif c == '\033':
            esc = True
        else:
            rc += 1
    return rc


def sprintf(format, *args):
    '''
    Alternative to the %-operator for strings, with support for '%n'
    
    @param   format:str                    The format string
    @param   args:*object                  The arguments to include in place of
                                           the placeholders in the format string
    @return  :(text:str, stops:list<int>)  The text after formatting, and locations of all '%n':s.
                                           Locations of '%n':s are measured using `len`, meaning that
                                           this function is aware of redefinitions of `len`.
    '''
    rc, measurements, curlen, esc, buf, args, argc = '', [], 0, False, '', tuple(args), 0
    for c in format:
        if esc:
            esc = False
            if c == 'n':
                buf %= args[:argc]
                curlen += len(buf)
                rc += buf
                buf = ''
                args = args[argc:]
                argc = 0
                measurements.append(curlen)
            else:
                buf += '%'
                buf += c
                argc += 1
        elif c == '%':
            esc = True
        else:
            buf += c
    rc += buf % args
    return (rc, measurements)


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
        self.last_return = None
    
    def __call__(self, *args, **kwargs):
        '''
        Invoke the function, every `interval`:th time
        
        @param   args:*?     The parameters of the function
        @param   kwargs:**?  The named parameters of the function
        @return  :¿R?        The return value of the function, the last return if not invoked
        '''
        rc = self.last_return
        if self.counter == 0:
            rc = self.function(*args, **kwargs)
            self.last_return = rc
            self.counter = self.interval
        self.counter -= 1
        return rc


class DelayedSometimes:
    '''
    Function wrapper for only actually invoking
    the function every n:th time, where n is a
    customisable parameter, with an added
    functionallity: the actual invocation will
    take place at the first invocation and then
    a number of invocations is required before
    the second actual invocation after which
    the normal interval will be used
    '''
    
    def __init__(self, function, delay, interval):
        '''
        Constructor
        
        @param  function:(*?)→¿R?  The functiony
        @param  delay:int          The of times needed to invoke between the first and second actual invocation
        @param  interval:int       Invoke the function every `interval`:th time
        '''
        def f(*args, **kwargs):
            self.function = Sometimes(function, interval, initial = delay)
            self.function.last_return = function(*args, **kwargs)
            return self.function.last_return
        self.function = f
    
    def __call__(self, *args, **kwargs):
        '''
        Invoke the function when scheduled
        
        @param   args:*?     The parameters of the function
        @param   kwargs:**?  The named parameters of the function
        @return  :¿R?        The return value of the function, the last return if not invoked
        '''
        return self.function(*args, **kwargs)


class Clocked:
    '''
    `Sometimes` wrapper that needs explicit re-evaluation before
    its `Sometimes` functionallity is invoked. That is, it needs
    a selected number of explicit re-evaluation before the value
    is actually re-evaluted.
    
    The rationale for this class is that you may want to update
    somethings more often than other things, periodically, but
    you may also want to update other things when certain events
    occur.
    '''
    
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        
        @param  args:*     Positional arguments for the `Sometimes` constructor
        @param  kwargs:**  Keyworkd arguments for the `Sometimes` constructor
        '''
        self.sometimes = Sometimes(*args, **kwargs)
        self.text = self.sometimes()
    
    
    def __call__(self, update = False):
        '''
        Return the most recently evaluated value
        
        @param   update:bool  Whether to re-evalute the value and return the new value
        @return  :¿T?         The most recently evaluated value
        '''
        if update:
            self.text = self.sometimes()
        return self.text
    
    
    @staticmethod
    def update_all(functions):
        '''
        Update all elements in an iteratable that is of the type `Clocked`
        
        @param  functions:itr<¿T?>  The iteratable
        '''
        for f in functions:
            if isinstance(f, Clocked):
                f(True)

