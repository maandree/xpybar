# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015  Mattias Andrée (maandree@member.fsf.org)

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

import solar_python


class Solar:
    '''
    Solar information
    '''
    
    
    SOLAR_ELEVATION_SUNSET_SUNRISE = 0.0
    '''
    :float  The Sun's elevation at sunset and sunrise,
            measured in degrees
    '''
    
    SOLAR_ELEVATION_CIVIL_DUSK_DAWN = -6.0
    '''
    :float  The Sun's elevation at civil dusk and civil
            dawn, measured in degrees
    '''
    
    SOLAR_ELEVATION_NAUTICAL_DUSK_DAWN = -12.0
    '''
    :float  The Sun's elevation at nautical dusk and
            nautical dawn, measured in degrees
    '''
    
    SOLAR_ELEVATION_ASTRONOMICAL_DUSK_DAWN = -18.0
    '''
    :float  The Sun's elevation at astronomical dusk
            and astronomical dawn, measured in degrees
    '''
    
    SOLAR_ELEVATION_RANGE_TWILIGHT = (-18.0, 0.0)
    '''
    :(float, float)  The Sun's lowest and highest elevation during
                     all periods of twilight, measured in degrees
    '''
    
    SOLAR_ELEVATION_RANGE_CIVIL_TWILIGHT = (-6.0, 0.0)
    '''
    :(float, float)  The Sun's lowest and highest elevation
                     during civil twilight, measured in degrees
    '''
    
    SOLAR_ELEVATION_RANGE_NAUTICAL_TWILIGHT = (-12.0, -6.0)
    '''
    :(float, float)  The Sun's lowest and highest elevation
                     during nautical twilight, measured in degrees
    '''
    
    SOLAR_ELEVATION_RANGE_ASTRONOMICAL_TWILIGHT = (-18.0, -12.0)
    '''
    :(float, float)  The Sun's lowest and highest elevation during
                     astronomical twilight, measured in degrees
    '''
    
    
    EQUINOX = 0
    SUMMER = 1
    WINTER = 2
    
    
    def __init__(self, latitude, longitude, t = None):
        '''
        Constructor
        
        @param  latitude:float   The latitude in degrees northwards from
                                 the equator, negative for southwards
        @param  longitude:float  The longitude in degrees eastwards from
                                 Greenwich, negative for westwards
        @param  t:float?         The time in Julian Centuries, `None`
                                 for the current time of when the functions
                                 are called
        '''
        self.lat = latitude
        self.lon = longitude
        self.t = t
        self.u = solar_python.julian_centuries_to_epoch
    
    
    def now(self):
        return solar_python.julian_centuries() if self.t is None else self.t
    
    
    def season(self):
        t = self.now()
        rc = Solar.SUMMER + solar_python.is_summer(self.lat, t)
        rc += Solar.WINTER + solar_python.is_winter(self.lat, t)
        return rc % 3
    
    
    def have_sunrise_and_sunset(self):
        '''
        Determine whether solar declination currently is
        so that there can be sunrises and sunsets. If not,
        you either have 24-hour daytime or 24-hour nighttime.
        
        @return  Whether there can be sunrises and sunsets where you are located
        '''
        return solar_python.have_sunrise_and_sunset(self.lat, self.now())
    
    
    def declination(self):
        '''
        Calculates the Sun's declination
        
        @return  :float   The Sun's declination, in degrees
        '''
        return solar_python.degrees(solar_python.solar_declination(self.now()))
    
    
    def elevation(self):
        '''
        Calculates the Sun's elevation as apparent
        from a geographical position
        
        @return  :float  The Sun's apparent at the specified time
                         as seen from the specified position,
                         measured in degrees
        '''
        return solar_python.solar_elevation(self.lat, self.lon, self.now())
    
    
    def future_equinox(self):
        '''
        Predict the time point of the next equinox
        
        @return  :float  The calculated time point, in POSIX time
        '''
        return self.u(solar_python.future_equinox(self.now()))
    
    
    def past_equinox(self):
        '''
        Predict the time point of the previous equinox
        
        @return  :float  The calculated time point, in POSIX time
        '''
        return self.u(solar_python.past_equinox(self.now()))
    
    
    def future_solstice(self):
        '''
        Predict the time point of the next solstice
        
        @return  :float  The calculated time point, in POSIX time
        '''
        return self.u(solar_python.future_solstice(self.now()))
    
    
    def past_solstice(self):
        '''
        Predict the time point of the previous solstice
        
        @return  :float  The calculated time point, in POSIX time
        '''
        return self.u(solar_python.past_solstice(self.now()))
    
    
    def future_elevation(self, elevation):
        '''
        Predict the time point of the next time the
        Sun reaches a specific elevation
        
        @param   elevation:float  The elevation of interest
        @return  :float?          The calculated time point, in POSIX time,
                                  `None` if none were found within a year
        '''
        return self.u(solar_python.future_elevation(self.lat, self.lon, elevation, self.now()))
    
    
    def past_elevation(self, elevation):
        '''
        Predict the time point of the previous time the Sun
        reached a specific elevation
        
        @param   elevation:float  The elevation of interest
        @return  :float?          The calculated time point, in POSIX time,
                                  `None` if none were found within a year
        '''
        return self.u(solar_python.past_elevation(self.lat, self.lon, elevation, self.now()))
    
    
    def future_elevation_derivative(self, derivative):
        '''
        Predict the time point of the next time the
        Sun reaches a specific elevation derivative
        
        @param   derivative:float  The elevation derivative value of interest
        @return  :float?           The calculated time point, in POSIX time,
                                   `None` if none were found within a year
        '''
        return self.u(solar_python.future_elevation_derivative(self.lat, self.lon, derivative, self.now()))
    
    
    def past_elevation_derivative(self, derivative):
        '''
        Predict the time point of the previous time
        the Sun reached a specific elevation derivative
        
        @param   derivative:float  The elevation derivative value of interest
        @return  :float?           The calculated time point, in POSIX time,
                                   `None` if none were found within a year
        '''
        return self.u(solar_python.past_elevation_derivative(self.lat, self.lon, derivative, self.now()))

