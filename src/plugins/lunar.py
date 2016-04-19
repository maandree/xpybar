# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016  Mattias Andrée (maandree@member.fsf.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import math
import time


class Lunar:
    '''
    Lunar observation
    
    @variable  fraction:float      The phase of the moon increasing linearly. 0 on new moon, 0,5 on
                                   full moon. ]0, 0,5[ when waxing and ]0m5, 1[ when waning.
    @variable  waxing:bool         `True` when moon is waxing (increasing illumination) and `False`
                                   when waning (decreasing). Not well defined on new moon (fraction = 0,
                                   illumination = 0) and full moon (fraction = 0,5, illumination = 1).
    @variable  terminator:float    The latitude, as seen from the northern hemisphere on Earth, of the
                                   terminator. The terminator is the line delimiting the sunlit area
                                   and the dark area.
    @variable  illumination:float  The illumnation of the moon, the fraction of the visible side's
                                   area that is sunlit
    '''
    
    REFERENCE_NEW_MOON = 934329600 # 11 August 1999 00:00:00 UTC
    '''
    :float  Time of last known new moon, in POSIX time
    '''
    
    SYNODIC_MONTH = 29.530588853
    '''
    :float  The length of a lunar month, in days
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        julian_day = lambda t   : t / 86400.0 + 2440587.5
        radians    = lambda deg : deg * math.pi / 180
        hacoversin = lambda deg : 0.5 - math.sin(radians(deg)) / 2
        
        ref = julian_day(Lunar.REFERENCE_NEW_MOON)
        now = julian_day(time.time())
        
        # TODO how to we calculate the Moon's apparent geocentric celestial longitude
        self.fraction = ((now - ref) / Lunar.SYNODIC_MONTH) % 1
        self.waxing = self.fraction <= 0.5 # we get an off by one without equality
        
        self.terminator = 90 - 360 * self.fraction # sunlit trailing
        if self.terminator < -90:
            self.terminator += 180 # visible side
        
        inverted = self.terminator < 0
        self.illumination = hacoversin(abs(self.terminator))
        if (not self.waxing) != inverted:
            self.illumination = 1 - self.illumination


# TODO add libration
# TODO add phase names
# TODO add solar and lunar eclipses
# TODO add position of sunlit area
# TODO add tides
# TODO add blue moon
# TODO add black moon
# TODO add moon colour
# TODO add altitude
# TODO add azimuth
# TODO add zodiac sign
# TODO add distances
# TODO add angular diameters

