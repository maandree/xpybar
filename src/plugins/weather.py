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


class Weather:
    '''
    Weather monitor
    
    @variable  icao:str               The station's International Civil Aviation Organization airport code
    @variable  station:str            The station as a human readable, not necessarily only the airport name
    @variable  location:str           Human readable location, country or state (abbreviated) and country.
    @variable  latitude:float         The latitude position of the station, in degrees to north with two decimals
    @variable  longitude:float        The longitude position of the station, in degrees to east with two decimals
    @variable  headers:list<str>      Headers in the decoded metar data
    @variable  fields:dict<str, str>  Fields in the decoded metar data
    @variable  time:(int, int, int)   The time observation was made: day of month, hour and minute, in UTC
    
    The following will be `None` if not found in the data, but it is probably found if it should not be `None`.
    They can be floating point, but are most often integers.
    
    @variable  wind_dir:float?           The wind direction, `None` if variable
    @variable  wind_speed:float          The wind speed in knots
    @variable  wind_gusts:float?         The wind gusts (variability of the wind speed) in knots
    @variable  wind_var:(float, float)?  The wind direction range, `None` if less than 60° variation
    @variable  temp:float                The temperature in °C
    @variable  dew:float                 The dew point in °C
    @variable  pressure:flaot            The pressure in hPa
    @variable  visibility:float          The visibility in statute miles
    '''
    
    
    def __init__(self, station):
        '''
        Constructor
        
        @param  station:str  The station's ICAO code (International Civil Aviation Organization airport code)
        '''
        self.icao = station
        url = 'http://weather.noaa.gov/pub/data/observations/metar/decoded/%s.TXT' % station
        decoded = spawn_read('wget', url, '-O', '-').split('\n')
        # How to parse: http://www.wunderground.com/metarFAQ.asp
        
        station_header, self.headers, decoded = decoded[0].split(', '), decoded[:2], decoded[2:]
        self.station, station_header = station_header[0], ', '.join(station_header[1:])
        self.location = station_header.split(' (')[0]
        self.latitude, self.longitude = station_header.split(') ').split(' ')[2:]
        self.latitude, ysign = self.latitude[:-1], self.latitude[-1] == 'S'
        self.longitude, xsign = self.longitude[:-1], self.longitude[-1] == 'W'
        self.latitude = [float(x) for x in self.latitude.split('-')]
        self.longitude = [float(x) for x in  self.longitude.split('-')]
        self.latitude = self.latitude[0] + self.latitude[1] / 100
        self.longitude = self.longitude[0] + self.longitude[1] / 100
        self.latitude = -(self.latitude) if ysign else self.latitude
        self.longitude = -(self.longitude) if xsign else self.longitude
        
        self.fields = {}
        for line in decoded:
            line = line.split(': ')
            self.fields[line[0]] = ': '.join(line[1:])
        
        self.wind_dir, self.wind_speed, self.wind_gusts, self.wind_var = None, None, None, None
        self.temp, self.dew, self.pressure, self.visibility            = None, None, None, None
        
        for ob in self.fields['ob'].split(' ')[1:]:
            self.__time(ob)
            self.__wind(ob)
            self.__wind_var(ob)
            self.__temp(ob)
            self.__pressure(ob)
            self.__visibility(ob)
            # (-SHRA)-Present Weather and Obscurations  from  http://www.wunderground.com/metarFAQ.asp (p44)
            # BKN070-Sky Condition                      from  http://www.wunderground.com/metarFAQ.asp
            # (p46, p49, p59(7,8,9). p61-65, p67-77, p91+96)
        
        #Wind: from the N (010 degrees) at 18 MPH (16 KT):0
        #Visibility: 3 mile(s):0
        #Sky conditions: overcast
        #Weather: precipitation
        #Precipitation last hour: A trace  -- sometimes
        #Temperature: 10.0 F (-12.2 C)
        #Windchill: -7 F (-22 C):2  -- sometimes
        #Dew Point: 3.9 F (-15.6 C)
        #Relative Humidity: 75%
        #Pressure (altimeter): 30.19 in. Hg (1022 hPa)
    
    
    def __time(self, ob):
        ob_ = list(filter(lambda c : not ('0' <= c <= '9'), ob))
        if (len(ob_) == 1) and ob.endswith('Z'):
            self.time = (ob[0 : 2], ob[2 : 4], ob[4 : 6])
    
    def __wind(self, ob):
        if ob.endswith('KT'):
            self.wind_dir = None if ob.startswith('VRB') else float(ob[:3])
            ob = ob[3:]
            i = ob.find('G') if 'G' in ob else ob.find('K')
            self.wind_speed, ob = float(ob[:i]), wind[i:]
            self.wind_gusts = float(ob[1 : -2]) if ob[0] == 'G' else None
    
    def __wind_var(self, ob):
        if (len(ob) == 7) and (ob[3] == 'V'):
            if len(list(filter(lambda c : not ('0' <= c <= '9'), ob))) == 1:
                self.wind_dir = (float(ob[:3]), float(ob[-3:]))
    
    def __temp(self, ob):
        if '/' in ob:
            ob = ob.replace('M', '-')
            if len(list(filter(lambda c : not ('0' <= c <= '9'), ob.replace('-', '0')))) == 1:
                (self.temp, self.dew) = [float(x) for x in ob.split('/')]
    
    def __pressure(self, ob):
        if (len(ob) == 5) and (ob[0] in ['Q', 'A']):
            if len(list(filter(lambda c : not ('0' <= c <= '9'), ob))) == 1:
                if ob[0] == 'Q':
                    self.pressure = float(ob[1:])
                else:
                    self.pressure = 33.86 * float(ob[1:]) / 100
    
    def __visibility(self, ob):
        # TODO p61
        if ob.endswith('SM') and (len(ob) > 0):
            if len(list(filter(lambda c : not ('0' <= c <= '9'), ob))) == 2:
                self.visibility = float(ob[:-2])
