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
    
    theme_preferences = ['hicolor', ..., 'ContrastHigh']
    '''
    :list<str|...>   List of themes in order of preference, `...` marks any that is not listed
    '''
    
    
    def __init__(self, file, background = 'black', width = None, height = None, icon = True):
        '''
        Constructor
        
        @param  file:str        The pathname of the image
        @param  background:str  ImageMagick understandable string for the background colour
        @param  width:int?      The width the image should have, `None` to not resize or use `height`
        @param  height:int?     The height the image should have, `None` to not resize or use `width`
        @parma  icon:bool       Whether to search for an icon among installed icons rather than
                                load the image via its pathname
        '''
        import Xlib.X, sys
        from subprocess import Popen, PIPE
        
        self.format = Xlib.X.ZPixmap
        self.depth = 24
        
        height = width if height is None else height
        width = height if width  is None else width
        raster = None
        
        if icon:
            file = Image.find_icon(file, width, height, Image.theme_preferences)
            if file is None:
                raise Exception('No icon found')
        
        # ImageMagick (and GraphicsMagick) forces white background when converting SVG images
        # so we need to sue rsvg-convert if we encounter an SVG image.
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
            self.data.append(buf[i + 2])
            self.data.append(buf[i + 1])
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
    
    
    @staticmethod
    def find_icon(name, width, height, preferences):
        '''
        Find and image for in abstract icon
        
        @param   name:str                    The name of the icon
        @param   width:int?                  The preferred width of the icon, `None` for as large as possible
        @param   height:int?                 The preferred height of the icon, `None` for as large as possible
        @param   preferences:list<str|...>   List of themes in order of preference, `...` marks any that is not listed
        @return  :str?                       A pathname for the icon, `None` if none found
        '''
        import os, pwd
        directories = []
        home = pwd.getpwuid(os.getuid()).pw_dir
        directories.append('%s/.icons' % home)
        if 'HOME' in os.environ:
            if not os.environ['HOME'] == home:
                home = os.environ['HOME']
                directories.append('%s/.icons' % home)
        directories += ['/usr/local/share/icons', '/usr/share/icons', '/share/icons']
        directories = [d for d in directories if os.path.exists(d) and os.path.isdir(d)]
        
        height = width if height is None else height
        width = height if width  is None else width
        
        dname = name.split('/')[0] if '/' in name else None
        iname = name.split('/')[-1]
        preferred_size = (width + height) // 2 if width is not None else None
        
        def order_themes(themes):
            themes, pre, post, state = set(themes), [], [], 0
            for theme in preferences:
                if theme is ...:
                    state = 1
                elif theme in themes:
                    themes.remove(theme)
                    (pre if state == 0 else post).append(theme)
            return pre + ([] if state == 0 else list(themes)) + post
        
        def order_sizes(sizes):
            sizes = [t(lambda : int(s.split('x')[0]), -1) for s in sizes]
            if preferred_size is not None:
                high = [s for s in sizes if (s > 0) and (s >= preferred_size)]
                low  = [s for s in sizes if (s > 0) and (s <  preferred_size)]
                high.sort()
                low.sort()
                high = ['%ix%i' % (s, s) for s in high]
                low  = ['%ix%i' % (s, s) for s in reversed(low)]
                return high + ['scalable'] + low
            else:
                sizes.sort()
                return ['scalable'] + reversed(sizes)
        
        def t(f, default):
            try:
                return f()
            except:
                return default
        
        def check(file):
            return ('.'.join(file.split('.')[:-1]) if '.' in file else file) == name
        
        def find_best(directory):
            j = lambda *f : '/'.join(list(f))
            for theme in order_themes(t(lambda : os.listdir(directory), [])):
                for size in order_sizes(t(lambda : os.listdir(j(directory, theme)), [])):
                    if dname is not None:
                        categories = [dname]
                    else:
                        categories = t(lambda : os.listdir(j(directory, theme, size)), [])
                    for cat in ['.'] + categories:
                        dir = j(directory, theme, size, cat)
                        files = t(lambda : os.listdir(dir), [])
                        files = [j(dir, f) for f in files if check(f)]
                        files = [f for f in files if os.path.isfile(f)]
                        if len(files) > 0:
                            files.sort()
                            return files[0]
            return None
        
        best = [(f, d) for f, d in zip([find_best(d) for d in directories], directories) if f is not None]
        if len(best) == 0:
            return None
        
        best = [(f, t(lambda : int(f[len(d):].split('/')[2]).split('x')[0], -1)) for f, d in best]
        max_size = 1 + max(s for _f, s in best)
        best = [(f, max_size if s < 0 else s) for (f, s) in best]
        if preferred_size is None:
            preferred_size = max_size
        
        high = [(f, s) for f, s in best if (s >= preferred_size)]
        low  = [(f, s) for f, s in best if (s <  preferred_size)]
        high.sort()
        low.sort()
        high = [(f, s) for f, s in high]
        low  = [(f, s) for f, s in reversed(low)]
        best = high + low
        
        return best[0][0]

