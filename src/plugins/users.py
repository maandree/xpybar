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

import os

from util import *


class Users:
    '''
    Gets the logged in users and what TTY:s they are using
    
    @variable  users:dict<str, list<str>>  Map from logged in users to acquired TTY:s (all might not be listed)
    '''
    
    
    def __init__(self, method = 'devfs'):
        '''
        Constructor
        
        @param  method:str|()→itr<str>  The user listing method
        '''
        users = Users.who
        if not isinstance(method, str):
            users = method
        elif method == 'who':    users = Users.who
        elif method == 'w':      users = Users.w
        elif method == 'devfs':  users = Users.devfs
        
        users = users()
        self.users = {}
        for (user, tty) in users:
            if user not in self.users:
                self.users[user] = []
            self.users[user].append(tty)
    
    
    @staticmethod
    def who():
        '''
        Use Coreutil's `who` command to fetch users and ttys
        
        @return  :list<(user:str, tty:str>)  List of user–tty pairs
        '''
        users = spawn('who').read().decode('utf-8', 'replace').split('\n')[:-1]
        users = [list(filter(lambda cell : not cell == '', line.split(' ')))[:2] for line in users]
        return users
    
    
    @staticmethod
    def w():
        '''
        Use procps-ng's `w` command to fetch users and ttys
        
        @return  :list<(user:str, tty:str>)  List of user–tty pairs
        '''
        users = spawn('w').read().decode('utf-8', 'replace').split('\n')[2 : -1]
        users = [list(filter(lambda cell : not cell == '', line.split(' ')))[:2] for line in users]
        return users
    
    
    @staticmethod
    def devfs(try_to_find_root = False):
        '''
        Walk /dev to find TTY acquisitions
        
        @param   try_to_find_root:bool       Whether to list root for /dev/tty[[:numeric:]]+ if the permission bits looks good
        @return  :list<(user:str, tty:str>)  List of user–tty pairs
        '''
        import pwd
        
        def num(s):
            return (not s == '') and (0 == len(list(filter(lambda c : not ('0' <= c <= '9'), s))))
        
        ttys = [f for f in os.listdir('/dev') if f.startswith('tty') and num(f[3:])]
        ttys += ['pts/' + f for f in os.listdir('/dev/pts') if num(f)]
        
        users, rc = {}, []
        for tty in ttys:
            try:
                attr = os.stat('/dev/' + tty)
            except:
                continue
            if ('/' not in tty) and (attr.st_uid == 0):
                if not (try_to_find_root and (attr.st_mode == 0o20600)):
                    continue
            user = attr.st_uid
            if user in users:
                user = users[user]
            else:
                try:
                    users[user] = user = pwd.getpwuid(user).pw_name
                except:
                    users[user] = user = str(user)
            rc.append((user, tty))
        return rc

