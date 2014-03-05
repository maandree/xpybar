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

import math
import time


def julian_day(t):
    '''
    Converts a POSIX time timestamp to a Julian Day timestamp
    
    @param   t:float  The time in POSIX time
    @return  :float   The time in Julian Days
    '''
    return t / 86400.0 + 2440587.5

def radians(deg):
    '''
    Convert an angle from degrees to radians
    
    @param   deg:float  The angle in degrees
    @return  :float     The angle in radians
    '''
    return deg * math.pi / 180

ref = julian_day(934329600) # 11 August 1999 00:00:00 UTC
now = julian_day(time.time())
synodic_month = 29.530588853

# TODO how to we calculate the Moon's apparent geocentric celestial longitude
fraction = ((now - ref) / synodic_month) % 1
waxing = fraction <= 0.5 # we get an off by one without equality
print('fraction: %f' % fraction)
print('waxing' if waxing else 'waning')

terminator = 90 - 360 * fraction # sunlit trailing
if terminator < -90:
    terminator += 180 # visible side
print('terminator: %f°' % terminator)

hacoversin = lambda deg : 0.5 - math.sin(radians(deg)) / 2

inverted = terminator < 0
illumination = hacoversin(abs(terminator))

if (not waxing) != inverted:
    illumination = 1 - illumination

print('illumination: %.2f%%' % (illumination * 100))

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

