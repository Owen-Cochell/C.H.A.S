# A simple Music player for C.H.A.S

from chaslib.extension import Extension
from chaslib.resptools import keyword_find, key_sta_find
from random import shuffle, randint
from chaslib.soundtools import WavePlayer
import pyaudio
import os
import json
import threading

# Potential inputs:
# 1. 'play Spanish Flea'
# Will search through every file until match is found
# 2. 'play Spanish Flea by Herb Albert
# Will search for Spanish Flea in folder Herb Albert
# 3. play  playlist Jams
# Will play playlist Jams
# 4. play Spanish Flea in Jams
# Will play Spanish Flea in playlist Jams


class MusicPlayer(Extension):

    def __init__(self):

        super(MusicPlayer, self).__init__('Music Player', 'A simple Music Player')
        self.chunk = 1024  # Chunksize
        self.p = pyaudio.PyAudio()  # Pyaudio instance
        self.stream = None  # Pyaudio stream
        self.wf = None  # Variable containing Wavefile
        self.wav = None  # Wave player instance
        self.media = self.chas.settings.media_dir  # Uses Default Media directory upon startup
        self.cache = []  # To be used to cache songs for quick playing
        self.playing = False  # Boolean determining if we are playing a song
        self.playlist_path = None  # Path to playlist file
        self.playlist = []  # Dictionary of playlist
        self.playlist_num = 0  # Current song index in playlist
        self.repeat = False  # Function determining if playlist repeats
        self.song = None  # Name of current song
        self.song_path = None  # Path to current song
        self.thread = None  # Threading object

    def match(self, mesg, talk, win):

        if key_sta_find(mesg, ['stop song', 'stop playlist', 'stop']):

            self.stop_song()

            win.add('Stopping audio...')

            return True

        if keyword_find(mesg, 'play'):

            # Wants us to play a song

            play_index = mesg.index('play')

            if keyword_find(mesg, 'by', start=play_index):

                # User wants to look in specific folder:

                index = mesg.index(' by ')

                title = mesg[play_index+5:index]
                print("Title: {}".format(title))
                song_dir = mesg[index+4:]

                out = self.search_song(title, foulder=song_dir)

                if not out:

                    # Song was not found :(

                    win.add("Song not found")

                    return False

                self.start_play()

                return True, f"Playing: {title}"

            if keyword_find(mesg, 'in', start=play_index):

                # User wants specific song in specific playlist:

                index = mesg.index(' in ')

                song_title = mesg[play_index+5:index]
                playlist_title = mesg[index+4:]

                out = self.search_playlist(playlist_title)

                if not out:

                    # Could not find playlist :(

                    win.add("Could not find playlist")

                    return False

                out = self.playlist_parse(song=song_title)

                if not out:

                    # Song not in playlist:

                    win.add("Song not in playlist")

                    return False

                self.start_player()

                win.add("Playing {} in {}".format(song_title, playlist_title))

                return True

            if keyword_find(mesg, 'playlist', start=play_index):

                title = mesg.index('playlist') + 9

                out = self.search_playlist(mesg[title:])

                if not out:

                    # Did not find playlist

                    win.add("Could not find playlist")

                    return False

                out = self.playlist_parse()

                if not out:

                    # Error parsing playlist:

                    win.add("Error parsing playlist")

                    return False

                self.start_player()

                win.add("Playing playlist {}".format(title))

                return True

            # Looking for song match/playlist:

            title = mesg[play_index+5:]

            if self.search_song(title):

                # Found Song
                self.start_play()

                win.add("Playing {}".format(title))

                return True

            if self.search_playlist(title):

                self.playlist_parse()
                self.start_player()

                win.add("Playing playlist {}".format(title))

                return True

        elif self.playlist:

            # Playlist methods

            if key_sta_find(mesg, ['next song', 'song up one']):

                # Function for iterating playlist:

                self.playlist_incriment(1)

                self.wav.stop()

                win.add("Playing next song")

                return True

            if key_sta_find(mesg, ['previous song', 'song down one']) and self.playlist is not []:

                self.playlist_incriment(-1)

                win.add("Playing previous song")

                return True

            if keyword_find(mesg, 'shuffle') and self.playlist is not []:

                # User wants to shuffle playlist:

                self.playlist_shuffle()

                win.add("Shuffling playlist")

                return True

            if keyword_find(mesg, 'restart') and self.playlist is not []:

                # User wants to restart playlist:

                self.playlist_restart()

                win.add("Restarting playlist")

                return True

            if keyword_find(mesg, 'random') and self.playlist is not []:

                # User wants random song in playlist

                self.playlist_random()

                win.add("Playing random song in playlist")

                return True

        elif self.playing:

            # Song commands:

            if key_sta_find(mesg, ['previous song', 'song down one', 'replay', 'repeat']):

                # User wants to replay last song:

                self.stop_song()
                self.play()

                win.add("Playing previous song")

                return True

            if keyword_find(mesg, 'add'):

                # User wants to add song to playlist:

                playlist_index = mesg.index(' to ') + 4

                playlist_title = mesg[playlist_index:]

                self.playlist_add(playlist_title)

                win.add("Adding song to playlist {}".format(playlist_title))

                return True

        return False

    def search_song(self, title, foulder=None):

        # This function will search for songs:

        temp_title = title.lower().replace(' ', '_') + '.wav'

        media_dir = os.path.join(self.media, 'songs/')

        if foulder is not None:

            foulder = foulder.lower().replace(' ', '_')
            media_dir = os.path.join(media_dir, foulder + '/')

        for root, dirs, files in os.walk(media_dir):

            if temp_title in files:

                # Found our song and returning path:

                self.song = title
                self.song_path = root + '/' + temp_title
                return True

        # Did not find song. Returning nothing

        return False
 
    def search_playlist(self, title, return_vals=False):

        # Function for searching for playlist:

        temp_dir = os.path.join(self.media, 'songs/playlists/')

        temp_title = title.lower().replace(' ', '_') + '.txt'

        for root, dirs, files in os.walk(temp_dir):

            if temp_title in files:

                # Found playlist, returning path:

                path = root + '/' + temp_title

                if return_vals:

                    # Returning vals instead of setting instance vars:

                    return path, True

                self.playlist_path = path

                return True

        # Did not find playlist.

        if return_vals:

            return None, False

        return False

    def playlist_parse(self, song=None):

        # User wants to use a playlist
        # Parsing playlist:

        file = open(self.playlist_path, 'r')

        lines = file.read().splitlines()

        for i in range(len(lines)):

            line = json.loads(lines[i])

            if song is not None and line['name'].lower() == song.lower():

                # We found our song!

                self.song = line['name']
                self.song_path = os.path.join(self.media, line['path'])
                self.playlist_num = i

            self.playlist.append(line)

        if song is not None and self.playlist_num is None:

            # Song not found:

            self.playlist = []
            self.playlist_path = None
            return False

        return True

    def play(self):

        # Function for Playing audio
        # Must be executed in thread

        self.wav = WavePlayer(

            self.chas,
            path=self.song_path,
            net=True

        )

        self.wav.start()

        self.playing = True

        return

    def start_play(self):

        # Function for starting play thread

        self.thread = threading.Thread(target=self.play, daemon=True)
        self.thread.start()
        return

    def player(self):

        # Function for iterating over playlist

        self.playing = True

        if self.song is None:

            # No song queued up, selecting first song:

            self.playlist_num = 0

        while self.playlist_num <= len(self.playlist) - 1:

            temp_num = self.playlist_num
            self.song = self.playlist[self.playlist_num]['name']
            self.song_path = os.path.join(self.media, self.playlist[self.playlist_num]['path'])

            self.play()

            self.wav.block()

            if not self.playing:

                # Stop playing song:

                break

            if temp_num != self.playlist_num:

                # User changed playlist index

                continue

            self.playlist_num = self.playlist_num + 1

            if self.playlist_num > len(self.playlist) - 1 and self.repeat:

                self.playlist_num = 0

        self.playlist = []
        self.playlist_num = 0
        self.playing = False

        return

    def start_player(self):

        # Function for starting player thread

        self.thread = threading.Thread(target=self.player, daemon=True)
        self.thread.start()
        return

    def playlist_incriment(self, num):

        val = self.playlist_num + num

        if val < 0 or val > len(self.playlist) - 1:

            # Invalid index!

            print("Invalid index!")

            return

        self.playlist_num = self.playlist_num + num
        self.wav.stop()
        return

    def playlist_shuffle(self):

        # Function for shuffling playlist:

        shuffle(self.playlist)

        return

    def playlist_restart(self):

        # User wants to restart playlist:

        self.playlist_parse()
        self.playlist_num = 0

        if self.playing:

            self.wav.stop()

        else:

            self.start_player()

        return

    def playlist_random(self):

        # Chooses random song from playlist:

        self.playlist_num = randint(0, len(self.playlist) - 1)
        self.wav.stop()

        return

    def playlist_add(self, playlist, title=None):

        # Function for adding song to playlist:

        temp_title = self.song
        temp_path = self.song_path.replace(self.media, '')

        playlist_path, val = self.search_playlist(playlist, return_vals=True)

        if not val:

            # Playlist not found
            print("Playlist not found")
            return False

        file = open(playlist_path, 'a')

        data = {"name": temp_title, "path": temp_path}

        file.write('\n' + str(json.dumps(data)))
        file.close()

        return

    def stop_song(self):

        if not self.playing:
            
            # Already stopped
        
            return

        self.song = None
        self.playlist_num = 0
        self.playing = False
        self.playlist = []

        self.wav.stop()

        self.wav = None

    def stop(self):

        self.wav.stop()
        self.p.terminate()
