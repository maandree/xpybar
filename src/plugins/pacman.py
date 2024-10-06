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

from util import *


class Pacman:
    '''
    Retrieve package information using Arch Linux's pacman
    
    Unique variables for installed:
    
    @variable  required:list<str>                  Packages that require this package
    @variable  optrequired:list<str>               Packages that this package is optional for
    @variable  install_date:str                    The date and time the package was installed
    @variable  installed_explicitly:bool           Whether the package was installed explicitly
    @variable  install_script:bool                 Whether the package contains and install script
    
    Unique variables for not installed:
    
    @variable  repository:str                      The repository the package is located in
    @variable  download_size:float                 The download size of the package in kilobytes
    
    Common variables:
    
    @variable  name:str                            The name of the package
    @variable  version:str                         The version of the package
    @variable  description:str                     The description of the package
    @variable  architecture:str                    The microprocessor architecture of the package
    @variable  url:str                             The home URL of the project
    @variable  licenses:list<str>                  The licenses used by the package
    @variable  groups:list<str>                    Package groups the package is a member of
    @variable  provides:list<str>                  Packages the package provides
    @variable  depends:list<str>                   Packages the package depends on
    @variable  optdepends:list<(str, str?, bool)>  Optional packages for this package, stored as a tuple of:
                                                     The name of the package, the reason for using it,
                                                     and whether or not it is installed.
    @variable  conflicts:list<str>                 Packages the package conflicts with
    @variable  replaces:list<str>                  Packages the package replaces
    @variable  installed_size:float                The installed size of the package in kilobytes
    @variable  packager:str?                       The packager of the package, `None` if unknown
    @variable  build_date:str                      The date and time the package was built
    @variable  validated_by:list<str>              Methods used to validate the package's integrity
    '''
    
    
    def __init__(self, package, installed):
        '''
        Constructor
        
        @param  package:str     The name of the package, can be %repo/%name
        @param  installed:bool  Whether it is information about the installed version that should be fetched
        '''
        verb = '-Qi' if installed else '-Si' # -Sii and -Qii, while a bit different, would get us more info.
        info = spawn_read('env', 'LOCALE=C', 'pacman', verb, package).split('\n')
        if len(info) == 1:
            raise Exception('Package `%s\' is not installed' % package)
        
        last_field = None
        fields = {}
        
        for line in info:
            continued = line.startswith(' ')
            line = list(filter(lambda cell : not cell == '', line.split(' ')))
            colon = -1
            if not continued:
                for i in range(len(line)):
                    if line[i] == ':':
                        colon = i
                        break
            field = last_field
            if colon >= 0:
                last_field = field = ' '.join(line[:colon])
                line = line[colon + 1:]
            if field not in fields:
                fields[field] = []
            fields[field].append(line)
        
        
        word = lambda x : fields[x][0][0]
        text = lambda x : ' '.join(fields[x][0])
        plur = lambda x : list(filter(lambda w : not w == 'None', fields[x][0]))
        
        if installed:
            self.required             = plur('Required By')
            self.optrequired          = plur('Optional For')
            self.install_date         = text('Install Date')
            self.installed_explicitly = text('Install Reason') == 'Explicitly installed'
            self.install_script       = text('Install Script') == 'Yes'
        
        if not installed:
            self.repository    = word('Name')
            self.download_size = float(word('Download Size'))
        
        self.name           = word('Name')
        self.version        = word('Version')
        self.description    = text('Description')
        self.architecture   = word('Architecture')
        self.url            = text('URL')
        self.licenses       = plur('Licences')
        self.groups         = plur('Groups')
        self.provides       = plur('Provides')
        self.depends        = plur('Depends On')
        self.optdepends     = []
        optdepends_         = [' '.join(x) for x in fields['Optional Deps']]
        for deps in optdepends_:
            inst = deps.endswith(' [installed]')
            if installed:
                deps = deps[:-len(' [installed]')]
            if ': ' in deps:
                deps = deps.split(': ')
                name = deps[0]
                deps = ': '.join(deps[1:])
                self.optdepends.append((name, deps, inst))
            else:
                self.optdepends.append((deps, None, inst))
        self.conflicts      = plur('Conflicts With')
        self.replaces       = plur('Replaces')
        self.installed_size = float(word('Installed Size'))
        self.packager       = text('Packager')
        if self.packager == 'Unknown Packager':
            self.packager = None
        self.build_date     = text('Build Date')
        self.validated_by   = list(filter(lambda x : not x == 'Sum', plur('Validated By')))

