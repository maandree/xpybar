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


class Image:
    '''
    Images and icons
    '''
    
    
    def __init__(self, file, background = 'black', width = None, height = None):
        '''
        Constructor
        
        @param  file:str        The pathname of the image
        @param  background:str  ImageMagick understandable string for the background colour
        @param  width:int?      The width the image should have, `None` to not resize or use `height`
        @param  height:int?     The height the image should have, `None` to not resize or use `width`
        '''
        import Xlib.X, sys
        from subprocess import Popen, PIPE
        
        self.format = Xlib.X.ZPixmap
        self.depth = 24
        
        height = width if height is None else height
        width = height if width  is None else width
        raster = None
        
        convert = ['file', '-']
        convert = Popen(convert, stdin = open(file, 'rb'), stdout = PIPE, stderr = sys.stderr)
        if 'Scalable Vector Graphics' in convert.communicate()[0].decode('utf-8', 'replace'):
            convert = ['rsvg-convert', '-f', 'png']
            if width is not None:
                convert += ['-w', str(width), '-h', str(height)]
            convert = Popen(convert, stdin = open(file, 'rb'), stdout = PIPE, stderr = sys.stderr)
            raster = convert.communicate()[0]
            if not convert.wait() == 0:
                raise Exception('Image could not be converted')
        
        convert = ['convert', '-', '-background', background, '-alpha', 'remove', '-depth', '8']
        if width is not None:
            convert += ['-resize', '%ix%i!' % (width, height)]
        convert += ['ppm:-']
        convert = Popen(convert, stdin = PIPE if raster is not None else open(file, 'rb'),
                        stdout = PIPE, stderr = sys.stderr)
        if raster is not None:
            self.data = list(convert.communicate(raster)[0])
        else:
            self.data = list(convert.communicate()[0])
        if not convert.wait() == 0:
            raise Exception('Image could not be converted')
        
        self.width, self.height, state, comment = [], [], 0, False
        for i in range(len(self.data)):
            b = self.data[i]
            if comment:
                if b == ord('\n'):
                    comment = False
            elif b == ord('#'):
                comment = True
            elif b in (ord(' '), ord('\n')):
                if (state & 1) == 0:
                    continue
                state += 1
                if state == 4 * 2:
                    break
            else:
                state += 1 - (state & 1)
                if state == 2 * 1 + 1:
                    self.width.append(b)
                elif state == 2 * 2 + 1:
                    self.height.append(b)
        
        self.data, buf = [], self.data[i:]
        self.width  = int(bytes(self.width).decode('utf-8', 'strict'))
        self.height = int(bytes(self.height).decode('utf-8', 'strict'))
        
        i = 0
        for _i in range(len(buf) // 3):
            self.data.append(buf[i])
            self.data.append(buf[i + 1])
            self.data.append(buf[i + 2])
            self.data.append(0)
            i += 3
        self.data = bytes(self.data)
    
    
    def draw(self, bar, x, y):
        '''
        Draw the image on a bar
        
        @param  bar:Bar  The bar to draw the image on
        @param  x:int    The left position of the image
        @param  y:int    The top position of the image
        '''
        bar.window.put_image(bar.gc, x, y, self.width, self.height, self.format, self.depth, 0, self.data)

