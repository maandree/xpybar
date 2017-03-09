# -*- python -*-
'''
xpybar – xmobar replacement written in python
Copyright © 2014, 2015, 2016, 2017  Mattias Andrée (maandree@member.fsf.org)

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


class PowerSupply:
    '''
    Power supply monitor
    
    To calculate the time (in hours) until discharged:
    ```
    power_supply.get_charge() / power_supply.get_current()
    ```
    
    To calculate the time (in hours) until charged:
    ```
    (power_supply.get_charge_full() - power_supply.get_charge()) / power_supply.get_current()
    ```
    
    @variable  name:str                 The name of the power supply
    @variable  path:str                 The path to the power supply in /sys
    @variable  type:str?                The power supply type, or `None` if not found
                                        (this is most likely not the case), known possible values
                                        'Mains' and 'Battery'
    
    The following will probably be `None` for non-Battery power supplies
    
    @variable  manufacturer:str?        The manufacturer of the power supply, `None` if unknown
    @variable  model_name:str?          The model name of the power supply, `None` if unknown
    @variable  serial_number:str?       The serial number of the power supply, `None` if unknown
    @variable  technology:str?          The technology the power supply uses, `None` if unknown
    @variable  charge_full_design:int?  The charge (nAh) of the power supply at full capacity
                                        when the power supply supply is 100 % healthy,
                                        `None` if unknown of if not applicable
    @variable  voltage_min_design:int?  The minimum voltage (nV) when the power supply supply is
                                        100 % healthy, `None` if unknown of if not applicable
    '''
    
    def __init__(self, name):
        '''
        Constructor
        
        @param  name:str  The name of the power supply, you can find
                          the with `PowerSupplu.supplies`
        '''
        self.name = name
        self.path = '/sys/class/power_supply/' + name
        
        self.type = None
        if os.path.exists(self.path + '/type'):
            with open(self.path + '/type', 'rb') as file:
                self.type = file.read().decode('utf-8', 'strict')[:-1]
        
        self.manufacturer = None
        if os.path.exists(self.path + '/manufacturer'):
            with open(self.path + '/manufacturer', 'rb') as file:
                self.manufacturer = file.read().decode('utf-8', 'strict')[:-1]
        
        self.model_name = None
        if os.path.exists(self.path + '/model_name'):
            with open(self.path + '/model_name', 'rb') as file:
                self.model_name = file.read().decode('utf-8', 'strict')[:-1]
        
        self.serial_number = None
        if os.path.exists(self.path + '/serial_number'):
            with open(self.path + '/serial_number', 'rb') as file:
                self.serial_number = file.read().decode('utf-8', 'strict')[:-1]
        
        self.technology = None
        if os.path.exists(self.path + '/technology'):
            with open(self.path + '/technology', 'rb') as file:
                self.technology = file.read().decode('utf-8', 'strict')[:-1]
        
        self.charge_full_design = None
        if os.path.exists(self.path + '/charge_full_design'):
            with open(self.path + '/charge_full_design', 'rb') as file:
                self.charge_full_design = int(file.read().decode('utf-8', 'strict')[:-1])
        elif os.path.exists(self.path + '/energy_full_design'):
            with open(self.path + '/energy_full_design', 'rb') as file:
                self.charge_full_design = int(file.read().decode('utf-8', 'strict')[:-1])
        
        self.voltage_min_design = None
        if os.path.exists(self.path + '/voltage_min_design'):
            with open(self.path + '/voltage_min_design', 'rb') as file:
                self.voltage_min_design = int(file.read().decode('utf-8', 'strict')[:-1])
    
    def get_alarm():
        '''
        Get the alarm level
        
        @return  :int?  The alarm level, `None` if unknown or if unapplicable
        '''
        if os.path.exists(self.path + '/alarm'):
            with open(self.path + '/alarm', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        return None
    
    def get_capacity():
        '''
        Get the current capacity
        
        This is a rounded down version of `.get_charge() / .get_charge_full()`
        
        @param  :int?  The current capacity,
                       `None` if unknown or if unapplicable
        '''
        if os.path.exists(self.path + '/capacity'):
            with open(self.path + '/capacity', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        return None
    
    def get_capacity_level():
        '''
        TODO some information about what this is would be nice
        '''
        if os.path.exists(self.path + '/capacity_level'):
            with open(self.path + '/capacity_level', 'rb') as file:
                return file.read().decode('utf-8', 'strict')[:-1]
        return None
    
    def get_charge_full():
        '''
        Get the charge when the power supply is fully charged
        according to the last known charge as fully charged state
        
        @return  :int?  The charge in nAh when the power supply is fully charged,
                        `None` if unknown or if unapplicable
        '''
        if os.path.exists(self.path + '/charge_full'):
            with open(self.path + '/charge_full', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        if os.path.exists(self.path + '/energy_full'):
            with open(self.path + '/energy_full', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        return None
    
    def get_charge():
        '''
        Get the current charge
        
        @return  :int?  The current charge in nAh,
                        `None` if unknown or if unapplicable
        '''
        if os.path.exists(self.path + '/charge_now'):
            with open(self.path + '/charge_now', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        if os.path.exists(self.path + '/energy_now'):
            with open(self.path + '/energy_now', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        return None
    
    def get_current():
        '''
        Get the current current
        
        @return  :int?  The current current in nA, `None` if unknown
        '''
        if os.path.exists(self.path + '/current_now'):
            with open(self.path + '/current_now', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        elif os.path.exists(self.path + '/power_now') and os.path.exists(self.path + '/voltage_now'):
            with open(self.path + '/power_now', 'rb') as file:
                power = int(file.read().decode('utf-8', 'strict')[:-1])
            with open(self.path + '/voltage_now', 'rb') as file:
                voltage = int(file.read().decode('utf-8', 'strict')[:-1])
            return 1000000 * power / voltage
        return None
    
    def get_power():
        '''
        Get the current power
        
        @return  :int?  The current power in nW, `None` if unknown
        '''
        if os.path.exists(self.path + '/power_now'):
            with open(self.path + '/power_now', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        elif os.path.exists(self.path + '/current_now') and os.path.exists(self.path + '/voltage_now'):
            with open(self.path + '/current_now', 'rb') as file:
                current = int(file.read().decode('utf-8', 'strict')[:-1])
            with open(self.path + '/voltage_now', 'rb') as file:
                voltage = int(file.read().decode('utf-8', 'strict')[:-1])
            return voltage * current / 1000000
        return None
    
    def get_cycle_count():
        '''
        Get the battery's cycle count, that is, the full charge
        energy divided by the total used energy
        
        @param  :int?  The number of cycle, is often appear as zero,
                       `None` if unknown or if unapplicable
        '''
        if os.path.exists(self.path + '/cycle_count'):
            with open(self.path + '/cycle_count', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        return None
    
    def get_status():
        '''
        Get the current status
        
        @return  :str?  The current status, known values are
                        'Charging', 'Discharging' and 'Unknown',
                        `None` if unknown or if unapplicable
        '''
        if os.path.exists(self.path + '/status'):
            with open(self.path + '/status', 'rb') as file:
                return file.read().decode('utf-8', 'strict')[:-1]
        return None
    
    def get_voltage():
        '''
        Get the current voltage
        
        @return  :int?  The current voltage in nV, `None` if unknown
        '''
        if os.path.exists(self.path + '/voltage_now'):
            with open(self.path + '/voltage_now', 'rb') as file:
                return int(file.read().decode('utf-8', 'strict')[:-1])
        return None
    
    def is_online(self):
        '''
        Check whether the power supply is online
        
        @return  :bool?  Whether the power supply is online, `None` if unknown
        '''
        if os.path.exists(self.path + '/online'):
            with open(self.path + '/online', 'rb') as file:
                return file.read().decode('utf-8', 'strict') == '1\n'
        if os.path.exists(self.path + '/present'):
            with open(self.path + '/present', 'rb') as file:
                return file.read().decode('utf-8', 'strict') == '1\n'
        return False
    
    @staticmethod
    def supplies():
        '''
        Lists all available power supplies
        
        If the returned list is empty, you are probably running on a
        desktop (or more powerful machine such as a server) that only
        runs on mains (AC).
        
        @return  :list<str>  The name of all available power supplies
        '''
        return os.listdir('/sys/class/power_supply')

