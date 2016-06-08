# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016  Mattias Andrée (maandree@member.fsf.org)

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

import calendar

from util import *


class LeapSeconds:
    '''
    Leap second announcement monitor
    '''
    
    
    PRIMARY = 0
    '''
    The leap occurs in a primarily preferred time slot
    '''
    
    SECONDARY = 1
    '''
    The leap occurs in a secondarily preferred time slot
    '''
    
    OUT_OF_BAND = 2
    '''
    The leap occurs out of band, not in any preferred time slot
    '''
    
    
    def __init__(self):
        '''
        Constructor
        '''
        #url = 'http://maia.usno.navy.mil/ser7/leapsec.dat'
        url = 'http://oceandata.sci.gsfc.nasa.gov/Ancillary/LUTs/modis/leapsec.dat'
        announcements = spawn_read('curl', url)
        while not announcements.startswith(' '):
            announcements = '\n'.join(announcements.split('\n')[1:])
        while '  ' in announcements:
            announcements = announcements.replace('  ', ' ')
        announcements = announcements.replace('= ', '=').replace('=JD ', '=JD')
        announcements = [announcement.lstrip().split(' ') for announcement in announcements.split('\n')]
        test = lambda announcement : announcement.startswith('TAI-UTC=') or announcement.startswith('UTC-TAI=')
        announcements = [announcement[:3] + list(filter(test, announcement)) for announcement in announcements]
        MONTHS = { 'JAN' : 1
                 , 'FEB' : 2
                 , 'MAR' : 3
                 , 'APR' : 4
                 , 'MAY' : 5
                 , 'JUN' : 6
                 , 'JUL' : 7
                 , 'AUG' : 8
                 , 'SEP' : 9
                 , 'OCT' : 10
                 , 'NOV' : 11
                 , 'DEC' : 12
                 }
        DAYS_OF_MONTHS = [-1, 31, 28, 31, 30, 31, 30, 30, 31, 30, 31, 30, 31]
        def translate(announcement):
            announcement[0] = int(announcement[0])
            announcement[1] = MONTHS[announcement[1]]
            announcement[2] = int(announcement[2]) - 1
            if announcement[3].startswith('TAI-UTC='):
                announcement[3] = int(announcement[3].split('=')[1].split('.')[0])
            else:
                announcement[3] = -(int(announcement[3].split('=')[1].split('.')[0]))
            announcement.append(LeapSeconds.OUT_OF_BAND)
            if announcement[2] == 0:
                announcement[1] -= 1
                if announcement[1] == 0:
                    announcement[1] = 12
                    announcement[0] -= 1
                announcement[2] = DAYS_OF_MONTHS[announcement[1]]
                if announcement[2] == 2:
                    year = announcement[0]
                    if ((year % 4 == 0) and not (year % 100 == 0)) or (year % 400 == 0):
                        announcement[2] += 1
                if announcement[1] in (6, 12):
                    announcement[4] = LeapSeconds.PRIMARY
                elif announcement[1] in (3, 9):
                    announcement[4] = LeapSeconds.SECONDARY
            return announcement
        announcements = [translate(announcement) for announcement in announcements]
        for i in reversed(range(len(announcements) - 1)):
            announcements[i + 1][3] -= announcements[i][3]
        self.announcements = announcements[1:]
    
    
    def __len__(self):
        '''
        Get the number of available leap second announcements
        
        @return  The number of available leap second announcements
        '''
        return len(self.announcements)
    
    
    def __getitem__(self, index):
        '''
        Get a leap second announcement
        
        @param   index:int?     The index of the announcement, negative for reversed chronological indexing
        @return  :(year:int,    The year the leap second will occur or occurred (UTC)
                   month:int,   The month [1, 12] the leap second will occur or occurred (UTC)
                   day:int,     The day [1, 31] the leap second will occur or occurred (UTC)
                   posix:int,   The POSIX timestamp the leap will occur or occurred.
                                Keep in mind that POSIX time does not have leap seconds;
                                if `amount == 1` then this time will represent 00:00:00 at
                                the day directly after the day described by (`year`, `month`, `day`)
                   amount:int,  The number of leap seconds introduced, can be negative but not zero
                   annon:int)   Annonouncement class, either of:
                                LeapSeconds.PRIMARY, LeapSeconds.SECONDARY, LeapSeconds.OUT_OF_BAND
        '''
        (y, m, d, a, t) = self.announcements[index]
        s = 24 * 60 * 60 + a - 1
        if a > 0:
            s += 1
        s = calendar.timegm((y, m, d, 0, 0, s))
        return (y, m, d, s, a, t)

