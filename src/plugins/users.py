# -*- python -*-
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

from util import *


class Users:
    '''
    Gets the logged in users and what TTY:s they are using
    
    @variable  users:dict<str, list<str>>  Map from logged in users to acquired TTY:s
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        users = spawn('w').read().decode('utf-8', 'replace').split('\n')[2 : -1]
        users = [list(filter(lambda cell : not cell == '', line.split(' ')))[:2] for line in users]
        self.users = {}
        for (user, tty) in users:
            if user not in self.users:
                self.users[user] = []
            self.users[user].append(tty)

