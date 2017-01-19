# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016, 2017  Mattias Andrée (maandree@member.fsf.org)

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


class Chase:
    '''
    Does Chase have a job yet?
    
    @variable  status:bool?  Whether or not Chase have a job, `None` if information has not been fetched
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        self.status = None
    
    
    def update(self):
        '''
        Update the information
        
        @return  :bool  Whether information could be fetched
        '''
        command = ['curl', 'http://www.doeschasehaveajobyet.com']
        proc = subprocess.Popen(command, stderr = sys.stderr, stdout = subprocess.PIPE)
        page = proc.stdout.read()
        proc.wait()
        if proc.returncode == 0:
            page = page.decode('utf-8', 'replace').split('\n')
            page = filter(lambda line : line == 'NO', page)
            page = filter(lambda line : not line == 'NOVEMBER', page)
            self.status = len(list(page)) == 0
            return True
        return False

