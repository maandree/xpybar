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

import alsaaudio


class ALSA:
    '''
    ALSA volume controller
    
    @variable  cardindex:int          The index of the audio card
    @variable  cardname:str           The name of the audio card, will be
                                      'default' if the default audio card is selected
                                      using it's logical name or logical index
    @variable  mixername:str          The name of the mixer
    @variable  mixer:alsaaudio.Mixer  The mixer object used internally by this class
    '''
    
    
    ALL_CHANNELS = -1
    '''
    :int  Channel index that selects all available channels
    '''

    DEFAULT_CARD = -1
    '''
    :int  Logical index of the default audio card
    '''
    
    
    def __init__(self, card = -1, mixername = 'Master', *, cardindex = None):
        '''
        Constructor
        
        @param  card:int|str   The index or name of the audio card,
                               `ALSA.DEFAULT_CARD` (-1) or 'default' for the default card
        @param  mixername:str  The name of the mixer
        '''
        if card == -1 and cardindex is not None: # For backwards compatibility
            card = cardindex
        if isinstance(card, str):
            if card == 'default':
                card = -1
            else:
                card = alsaaudio.cards().index(card)
        self.cardindex = card
        self.mixername = mixername
        self.mixer = alsaaudio.Mixer(self.mixername, 0, self.cardindex)
        self.cardname = self.mixer.cardname
    
    
    def get_volume(self):
        '''
        Get the volume for each channel on the mixer
        
        @return  :list<int?>  The [0, 100] volume for each channel, `None` on a channel indicate that it is muted
        '''
        self.mixer = alsaaudio.Mixer(self.mixername, 0, self.cardindex)
        vs = self.mixer.getvolume()
        try:
            ms = self.mixer.getmute()
        except:
            ms = [0] * len(vs)
        return [v if m == 0 else None for (v, m) in zip(vs, ms)]
    
    
    def set_volume(self, volume, channel = -1):
        '''
        Set the volume for a channel on the mixer
        
        @param  volume:int?  The [0, 100] volume for the channel, `None` to mute the channel
        @param  channel:int  The index of the channel, `ALSA.ALL_CHANNELS` (-1) for all channels
        '''
        if volume is None:
            self.mixer.setmute(1, channel)
        else:
            self.mixer.setvolume(volume, channel)
            try:
                self.mixer.setmute(0, channel)
            except:
                pass # some mixers do not have mute switch
    
    
    def get_mute(self):
        '''
        Get the mute status for each channel on the mixer
        
        @return  :list<bool>  Whether mixer is muted for each channel
        '''
        self.mixer = alsaaudio.Mixer(self.mixername, 0, self.cardindex)
        try:
            return [m == 1 for m in self.mixer.getmute()]
        except:
            return [False] * len(self.mixer.getvolume())
    
    
    def set_mute(self, mute, channel = -1):
        '''
        Set the mute status on the mixer
        
        @param  mute:bool    Whether the mixer should be muted on the channel
        @param  channel:int  The index of the channel, `ALSA.ALL_CHANNELS` (-1) for all channels
        '''
        self.mixer.setmute(mute, channel)
    
    
    @staticmethod
    def get_cards():
        '''
        Get the names of all available audio cards
        
        @return  :list<str>  The names of all available audio cards
        '''
        return alsaaudio.cards()
    
    
    @staticmethod
    def get_mixers(card = -1, *, cardindex = None):
        '''
        Get the names of all available mixers for an audio card
        
        @param   card:int|str   The index or name of the audio card,
                                `ALSA.DEFAULT_CARD` (-1) or 'default' for the default card
        @return  :list<str>     The names of all available mixers for an audio card
        '''
        if card == -1 and cardindex is not None: # For backwards compatibility
            card = cardindex
        if isinstance(card, str):
            if card == 'default':
                card = -1
            else:
                card = alsaaudio.cards().index(card)
        return alsaaudio.mixers(card)

