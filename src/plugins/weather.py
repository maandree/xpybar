# -*- python -*-
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
    @variable  wind_gusts:float?         The wind gusts (variability of the wind speed; towards) in knots
    @variable  wind_var:(float, float)?  The wind direction range, `None` if less than 60° variation
    @variable  temp:float                The temperature in °C
    @variable  dew:float                 The dew point in °C
    @variable  wind_chill:float          The wind chill in °C
    @variable  humidity:float            The relative humidity in %
    @variable  pressure:flaot            The pressure in hPa
    @variable  visibility:float          The visibility in statute miles
    '''
    
    
    def __init__(self, station = None):
        '''
        Constructor
        
        @param  station:str?  The station's ICAO code (International Civil Aviation Organization airport code),
                              if `None`, ~/.config/metar or /etc/metar will be used (see metar(1))
        '''
        import os, pwd
        if station is None:
            try:
                filename = os.environ['HOME'] if 'HOME' in os.environ else ''
                if len(filename) == 0:
                    filename = pwd.getpwuid(os.getuid()).pw_dir
                filename = '%s/.config/metar' % filename
                if not os.path.isfile(filename):
                    filename = '/etc/metar'
            except:
                filename = '/etc/metar'
            with open(filename, 'rb') as file:
                station = file.read()
            station = station.decode('utf-8', 'strict').split('\n')[0]
        self.icao = station
        #url = 'http://weather.noaa.gov/pub/data/observations/metar/decoded/%s.TXT' % station
        url = 'https://tgftp.nws.noaa.gov/data/observations/metar/decoded/%s.TXT' % station
        decoded = spawn_read('curl', url).split('\n')
        # How to parse: http://www.wunderground.com/metarFAQ.asp
        
        station_header, self.headers, decoded = decoded[0].split(', '), decoded[:2], decoded[2:]
        self.station, station_header = station_header[0], ', '.join(station_header[1:])
        self.location = station_header.split(' (')[0]
        self.latitude, self.longitude = station_header.split(') ')[1].split(' ')[:2]
        self.latitude,  ysign = self.latitude[:-1],  self.latitude[-1]  == 'S'
        self.longitude, xsign = self.longitude[:-1], self.longitude[-1] == 'W'
        self.latitude  = [float(x) for x in self.latitude.split('-')]
        self.longitude = [float(x) for x in self.longitude.split('-')]
        self.latitude  = self.latitude[0]  + self.latitude[1]  / 100
        self.longitude = self.longitude[0] + self.longitude[1] / 100
        self.latitude  = -(self.latitude)  if ysign else self.latitude
        self.longitude = -(self.longitude) if xsign else self.longitude
        
        self.fields = {}
        for line in decoded:
            line = line.split(': ')
            self.fields[line[0]] = ': '.join(line[1:])
        
        self.wind_dir, self.wind_speed, self.wind_gusts     = None, None, None
        self.wind_var, self.temp, self.dew, self.wind_chill = None, None, None, None
        self.pressure, self.visibility, self.humidity       = None, None, None
        
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
        
        if 'Relative Humidity' in self.fields:
            try:
                self.humidity = float(self.fields['Relative Humidity'].replace('%', ''))
            except:
                pass
        
        get_celsius = lambda text : float(text.split('(')[1].split(')')[0])
        if 'Windchill' in self.fields:
            try:
                self.windchill = get_celsius(self.fields['Windchill'])
            except:
                pass
        if self.dew is None and 'Dew Point' in self.fields:
            try:
                self.dew = get_celsius(self.fields['Dew Point'])
            except:
                pass
        if self.temp is None and 'Temperature' in self.fields:
            try:
                self.temp = get_celsius(self.fields['Temperature'])
            except:
                pass
        
        #Wind: from the N (010 degrees) at 18 MPH (16 KT):0
        #Visibility: 3 mile(s):0
        #Sky conditions: overcast
        #Weather: precipitation
        #Precipitation last hour: A trace  -- sometimes
        #Windchill: -7 F (-22 C):2  -- sometimes
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
            self.wind_speed, ob = float(ob[:i]), ob[i:]
            self.wind_gusts = float(ob[1 : -2]) if ob[0] == 'G' else None
    
    def __wind_var(self, ob):
        if (len(ob) == 7) and (ob[3] == 'V'):
            if len(list(filter(lambda c : not ('0' <= c <= '9'), ob))) == 1:
                self.wind_var = (float(ob[:3]), float(ob[-3:]))
    
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

