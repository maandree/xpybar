/**
 * xpybar – xmobar replacement written in python
 * Copyright © 2014, 2015, 2016, 2017, 2018  Mattias Andrée (maandree@kth.se)
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <unistd.h>
#include <stdio.h>
#include <string.h>


int main(int argc, char** argv)
{
  char* act;
  int i;
  
  if (argc < 2)
    return 1;
  
  if (setuid(0))
    perror(*argv);
  
  act = argv[1];
  
  for (i = 2; i < argc; i++)
    if (argv[i][0] == '/')
      return 1;
  
  if (*act++ != '-')
    return 1;
  
  if      (!strcmp(act, "a"))  ;
  else if (!strcmp(act, "A"))  ;
  else if ( strstr(act, "B") == act)  ;
  else if (!strcmp(act, "c"))  ;
  else if (!strcmp(act, "C"))  ;
  else if (!strcmp(act, "g"))  ;
  else if (!strcmp(act, "H"))  ;
  else if (!strcmp(act, "i"))  ;
  else if (!strcmp(act, "I"))  ;
  else if ( strstr(act, "J") == act)  ;
  else if (!strcmp(act, "m"))  ;
  else if ( strstr(act, "M") == act)  ;
  else if (!strcmp(act, "N"))  ;
  else if (!strcmp(act, "Q"))  ;
  else if (!strcmp(act, "r"))  ;
  else if (!strcmp(act, "R"))  ;
  else if ( strstr(act, "S") == act)  ;
  else if (!strcmp(act, "W"))  ;
  else if (!strcmp(act, "y"))  ;
  else if (!strcmp(act, "Y"))  ;
  else if (!strcmp(act, "Z"))  ;
  else
    return 1;
  
  execv(HDPARM_PATH, argv);
  perror(*argv);
  
  return 1;
}

