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


class Swaps:
    '''
    Swap statistics
    
    @variable  headers:list<str>          The titles of the fields
    @variable  header_map:dict<str, int>  Map from field title to field index (the reverse of `headers`)
    @variable  swaps:list<list<str>>      List of swaps spaces, each element in this list is a list of
                                          fields identified by `headers`
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        with open('/proc/swaps', 'rb') as file:
            data = file.read()
        data = data.decode('utf-8', 'replace').rstrip('\n').replace('\t', ' ')
        data = data.split('\n')
        self.headers, self.swaps = Swaps.__split(data[0]), [Swaps.__split(line) for line in data[1:]]
        self.header_map = dict((t, i) for i, t in enumerate(self.headers))
    
    
    def refresh(self):
        '''
        Update the variable `swaps`
        '''
        with open('/proc/swaps', 'rb') as file:
            data = file.read()
        data = data.decode('utf-8', 'replace').rstrip('\n').replace('\t', ' ').split('\n')[1:]
        self.swaps = [Swaps.__split(line) for line in data]
    
    
    @staticmethod
    def __split(line):
        return [field for field in line.split(' ') if not field == '']

