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


class Application:
    '''
    Applications and .desktop files
    
    @variable  desktop_file:str                                 The .desktop file for the application
    @variable  settings:dict<str?, dict<str, dict<str?, str>>>  Section → key → locale → value map of settings
    '''
    
    
    def __init__(self, file):
        '''
        Constructor
        
        @param  file:str  The .desktop file if it contains '/', otherwise the name of the application
        '''
        import os
        if '/' not in file:
            import pwd
            directories = []
            home = pwd.getpwuid(os.getuid()).pw_dir
            directories.append('%s/.local/share/applications' % home)
            if 'HOME' in os.environ:
                if not os.environ['HOME'] == home:
                    home = os.environ['HOME']
                    directories.append('%s/.local/share/applications' % home)
            directories += ['/usr/local/share/applications', '/usr/share/applications', '/share/applications']
            directories = [d for d in directories if os.path.exists(d) and os.path.isdir(d)]
            
            file = ['%s/%s.desktop' % (d, file) for d in directories]
            file = [f for f in file if os.path.exists(f) and os.path.isfile(f)]
            if len(file) == 0:
                raise Exception('Application not found')
            file = file[0]
        
        self.desktop_file = file
        with open(self.desktop_file, 'rb') as file:
            data = file.read()
        data = [l for l in data.decode('utf-8', 'replace').replace('\r', '\n').split('\n') if not l == '']
        
        section = None
        self.settings = {}
        for line in data:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                section = line[1 : -1]
            elif line.startswith(';') or line.startswith('#'):
                pass
            elif (':' in line) or ('=' in line):
                line_e = line.split('=')
                line_c = line.split(':')
                if len(line_e[0]) < len(line_c[0]):
                    first = '='
                    line = line_e
                else:
                    first = ':'
                    line = line_c
                key, value = line[0].rstrip(), first.join(line[1:]).lstrip()
                locale = None
                if ('[' in key) and key.endswith(']'):
                    key = key[:-1].split('[')
                    key, locale = '['.join(key[:-1]), key[-1]
                if section not in self.settings:
                    self.settings[section] = {}
                section_map = self.settings[section]
                if key not in section_map:
                    section_map[key] = {}
                key_map = section_map[key]
                if locale not in key_map:
                    key_map[locale] = value
        
        self.locales = [None]
        if 'LANG' in os.environ:
            locale = os.environ['LANG']
        elif 'LOCALE' in os.environ:
            locale = os.environ['LOCALE']
        else:
            return
        locale = locale.split(' ')[0].split('.')[0].split('_')
        for i in range(len(locale)):
            self.locales.append('_'.join(locale[:i]))
        self.locales.reverse()
    
    
    def get_setting(self, key, section = 'Desktop Entry', locales = None):
        '''
        Read a setting in the application's .desktop file
        
        @param  key:str             The key
        @param  section:str?        The section where the key is located
        @param  locale:list<str?>?  Acceptable locales in order of preference,
                                    `None` to use the default for your locale
        '''
        map = self.settings
        if section not in map:
            return None
        map = map[section]
        if key not in map:
            return None
        map = map[key]
        if locales is None:
            locales = self.locales
        for locale in locales:
            if locale in map:
                return map[locale]
        return None
    
    
    @staticmethod
    def strip_placeholders(text):
        '''
        Remove placeholders form an exec string
        
        @param   text:str  The exec string with placeholders
        @return  :str      The exec string without placeholders
        '''
        buf, esc = '', False
        for c in text:
            if esc:
                esc = False
                if c == '%':
                    buf += c
            elif c == '%':
                esc = True
            else:
                buf += c
        return buf

