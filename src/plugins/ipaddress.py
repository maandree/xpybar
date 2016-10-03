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

import os

from util import *


class IPAddress:
    '''
    Multi-home aware retrieval of public and private IP addresses
    
    @variable  nics:dict<str,            The state and IP address for a network interface card
                         (state:int      Either of: `IPAddress.{DOWN,UNKNOWN,ISOLATED,UP}`
                          private:str?   The interface's private IPv4 address
                          private6:str?  The interface's private IPv6 address
                          public:str?)>  The interface's public IP address on the Internet
    '''
    
    
    DOWN = 0
    '''
    The network interface is down
    '''
    
    UNKNOWN = 1
    '''
    The network interface's public IP address is unknown,
    but it is connected to the Internet
    '''
    
    ISOLATED = 2
    '''
    The network interface's public IP address is unknown
    because it does not appear to be connected to the Internet
    '''
    
    UP = 3
    '''
    The network interface is up and the public IP address is known
    '''
    
    
    def __init__(self, *exclude):
        '''
        Constructor
        
        @param  exclude:*str  Devices to exclude
        '''
        nics = [d for d in os.listdir('/sys/class/net') if d not in exclude]
        infos = [i for i in spawn_read('ifconfig').split('\n\n') if not i == '']
        self.nics = {}
        for nic in nics:
            state, private, private6, public = IPAddress.DOWN, None, None, None
            for info in infos:
                if info.startswith(nic + ': '):
                    info = [i.lstrip().split(' ') for i in info.split('\n')[1:]]
                    info = dict((i[0], i[1]) for i in info if len(i) > 1)
                    private = info['inet'] if 'inet' in info else None
                    private6 = info['inet6'] if 'inet6' in info else None
                    state = IPAddress.ISOLATED
                    break
            if not state == IPAddress.DOWN:
                self.__isolated = True
                download = lambda page : ('curl', '--interface', nic, page)
                public = self.__site_0(download)
                if public is None:  public = self.__site_1(download)
                if public is None:  public = self.__site_2(download)
                if public is None:  public = self.__site_3(download)
                if public is None:  public = self.__site_4(download)
                if public is None:  public = self.__site_5(download)
                if public is None:  public = self.__site_6(download)
                if public is None:  public = self.__site_7(download)
                if public is None:  public = self.__site_8(download)
                if public is not None:
                    state = IPAddress.UP
                elif not self.__isolated:
                    state = IPAddress.UNKNOWN
            self.nics[nic] = (state, private, private6, public)
    
    
    def public(self):
        '''
        Get all unique public IP address
        
        @return  :dist<address:str?, nics:list<str>>  The IP addresses and the interfaces with those addresses
        '''
        rc = {}
        for nic in self.nics.keys():
            if self.nics[nic][3] in rc:
                rc[self.nics[nic][3]].append(nic)
            else:
                rc[self.nics[nic][3]] = [nic]
        return rc
    
    
    def __site_0(self, download):
        try:
            data = spawn_read(*download('http://checkip.dyndns.org'))
            if not data == '':
                self.__isolated = False
            return data.split('<body>')[1].split('</body>')[0].split(': ')[1]
        except:
            return None
    
    def __site_1(self, download):
        try:
            data = spawn_read(*download('http://ipecho.net/plain'))
            if not data == '':
                self.__isolated = False
            data = data.strip()
            return data if not data == '' else None
        except:
            return None
    
    def __site_2(self, download):
        try:
            data = spawn_read(*download('http://www.checkmyipaddress.org'))
            if not data == '':
                self.__isolated = False
            data = [line.strip() for line in data.replace('\r\n', '\n').split('\n') if '</h3>' in line]
            data = [line.split('>')[1].split('<')[0] for line in data]
            data = [line for line in data if ' ' not in line]
            return data[0] if not len(data) == 0 else None
        except:
            return None
    
    def __site_3(self, download):
        try:
            data = spawn_read(*download('http://www.ip-address.org'))
            if not data == '':
                self.__isolated = False
            data = [line.strip(' \t') for line in data.replace('\r\n', '\n').split('\n') if 'ip += ' in line]
            data = [line.split('"')[1] for line in data if len(line) - len(line.replace('"', '')) == 2]
            data = [line.split('<')[0] for line in data]
            data_ = []
            for line in data:
                line_ = line
                for c in '0123456789abcdefABCDEF.:':
                    line_ = line_.replace(c, '')
                if not line_ == '':
                    data_.append(line_)
            return data_[0] if not len(data_) == 0 else None
        except:
            return None
    
    def __site_4(self, download):
        try:
            data = spawn_read(*download('http://www.myipnumber.com/my-ip-address.asp'))
            if not data == '':
                self.__isolated = False
            data = data.replace('\r\n', '\n').split('\nThe IP Address of this machine is:\n')[1]
            return data.lower().split('\n')[0].split('<b>\n')[1].split('\n</b>')[0]
        except:
            return None
    
    def __site_5(self, download):
        try:
            data = spawn_read(*download('http://www.findipinfo.com'))
            if not data == '':
                self.__isolated = False
            return data.split('Your IP Address Is: ')[1].split('<')[0]
        except:
            return None
    
    def __site_6(self, download):
        try:
            data = spawn_read(*download('http://what-ip.net'))
            if not data == '':
                self.__isolated = False
            return data.split('Your IP Address is : ')[1].split('<b>')[1].split('</b>')[0]
        except:
            return None
    
    def __site_7(self, download):
        try:
            data = spawn_read(*download('http://my-ip-address.com'))
            if not data == '':
                self.__isolated = False
            return data.split('<input ')[1].split('>')[0].split('value=')[1].split('"')[1]
        except:
            return None
    
    def __site_8(self, download):
        try:
            data = spawn_read(*download('https://duckduckgo.com?q=what is my ip address'))
            if not data == '':
                self.__isolated = False
            return data.split('"Answer":"Your IP address is ')[1].split(' ')[0]
        except:
            return None

