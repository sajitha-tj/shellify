import os
import multiprocessing
import ctypes
import time
import json
import random
from modules.mini_cli_animator import Mini_cli_animator

"""
            ______________  _                         
           (_____________ \| |                        
 ____  ____   ____  _____) ) | ____ _   _  ____  ____ 
|    \|  _ \ (___ \|  ____/| |/ _  | | | |/ _  )/ ___)
| | | | | | |____) ) |     | ( ( | | |_| ( (/ /| |    
|_|_|_| ||_(______/|_|     |_|\_||_|\__  |\____)_|    ~v1.0
      |_|                          (____/             
"""

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # Hide the pygame support prompt
import pygame

class Mp3Player:
    def __init__(self, verbose_mode=True):
        self.current_playlist = None
        self.current_track_index = multiprocessing.Value('i', 0)
        self.current_track_name = multiprocessing.Value(ctypes.c_wchar_p, "track_name")
        self.current_track_path = multiprocessing.Value(ctypes.c_wchar_p, "")
        self.current_status_player = multiprocessing.Value('b', False)
        self.current_status_playlist = multiprocessing.Value('b', False)
        # self.current_player_process = None
        self.current_playlist_process = None
        self.current_play_mode = multiprocessing.Value('i', 0) # 0: normal, 1: loop, 2: shuffle
        self.verbose_mode = multiprocessing.Value('b', verbose_mode)
        self.is_playing = multiprocessing.Value('b', False)
    
    def core_track_play(self, track_path: str):
        '''
        Core function to play the track
        arguments: track_path: str
        returns  : None
        '''
        pygame.mixer.init() # Initialize pygame mixer
        pygame.mixer.music.load(track_path) # Load the mp3 file
        pygame.mixer.music.play() # Start playing the mp3 file
        self.is_playing.value = True
        # mini_anime = Mini_cli_animator()
        # mini_anime.animate_on_own(0.4)
        # Wait for the music to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(1)
            # mini_anime.animate()
        # mini_anime.stop()
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.is_playing.value = False
        return


    def stop_internal_player(self):
        '''
        Stop playing the current track
        arguments: None
        returns  : None
        '''
        if self.current_status_player.value:
            try:
                # self.current_player_process.terminate()
                self.current_status_player.value = False
                if self.verbose_mode.value: print("[+] Stopped the player.")
                self.is_playing.value = False
            except Exception as e:
                if self.verbose_mode.value: print(f"[!] Error: {e}")
        else:
            if self.verbose_mode.value: print("[!] Nothing playing.")
        return

    def play_path(self, path_to_track: str):
        '''
        Play the given track from the given path
        arguments: path_to_track: str
        returns  : process obj of the player
        '''
        if not path_to_track:
            if self.verbose_mode.value: print("[!] No path provided.")
            return
        if not os.path.exists(path_to_track):
            if self.verbose_mode.value: print("[!] File not found.")
            return
        if not path_to_track.endswith('.mp3'):
            if self.verbose_mode.value: print("[!] Not a valid mp3 file.")
            return
        # If there is a track playing, stop it first
        # if self.current_status_player.value:      #############
        #     self.current_player_process.terminate()    ########
        # Start playing the new track
        if self.verbose_mode.value: print(f"[+] Playing: {self.current_track_name.value}...")
        try:
            self.current_status_player.value = True
            # self.current_player_process = multiprocessing.Process(target=playsound.playsound, args=(path_to_track,), daemon=True)
            # self.current_player_process.run()
            # self.current_player_process = multiprocessing.Process(target=self.core_track_play, args=(path_to_track,), daemon=True)
            # self.current_player_process.run()
            self.core_track_play(path_to_track)
            if self.verbose_mode.value: print("[+] Track ended.")
            self.current_status_player.value = False
        except Exception as e:
            if self.verbose_mode.value: print(f"[!] Error: {e}")
        # return self.current_player_process
    
    def play(self, song:dict):
        '''
        Play the given track
        arguments: song: dict {'track_name': 'track1', 'file_path': 'path1'}
        returns  : process obj of the player
        '''
        if not song:
            if self.verbose_mode.value: print("[!] No track provided.")
            return
        track_name = song['track_name']
        track_path = song['file_path']
        self.current_track_name.value = track_name
        self.current_track_path.value = track_path
        return self.play_path(track_path)
    
    def core_playlist_play(self):
        '''
        Core function to play the playlist
        arguments: None
        returns  : None
        '''
        while self.current_track_index.value < len(self.current_playlist):
            song = self.current_playlist[str(self.current_track_index.value)]
            self.play(song)
            # self.current_player_process.join()
            self.current_track_index.value += 1
            # Check for play mode
            # 0: normal
            # 1: loop
            # 2: shuffle
            if self.current_play_mode.value == 0: # normal mode
                pass
            elif self.current_play_mode.value == 1: # loop mode
                if self.current_track_index.value >= len(self.current_playlist):
                    self.current_track_index.value = 0
            elif self.current_play_mode.value == 2: # shuffle mode
                self.current_track_index.value = random.randint(0, len(self.current_playlist) - 1)
            else:
                if self.verbose_mode.value: print("[!] Invalid play mode.")
                break
        return

    
    def play_configured_playlist_tracks(self):
        '''
        Play the configured playlist
        arguments: None
        returns  : None
        '''
        if not self.current_playlist:
            if self.verbose_mode.value: print("[!] No playlist configured.")
            return
        
        if self.current_status_playlist.value:
            self.current_playlist_process.terminate()
            self.current_status_playlist.value = False

        self.current_playlist_process = multiprocessing.Process(target=self.core_playlist_play)
        self.current_playlist_process.start()
        self.current_status_playlist.value = True
        return
    
    def play_next(self):
        '''
        Play the next track in the current playlist
        arguments: None
        returns  : None
        '''
        if not self.current_playlist:
            if self.verbose_mode.value: print("[!] No playlist provided.")
            return

        self.current_track_index.value += 1
        if self.current_track_index.value >= len(self.current_playlist):
            if self.verbose_mode.value: print("[!] End of playlist. Restarting from the beginning.")
            self.current_track_index.value = 0
        if self.verbose_mode.value: print(f"[+] Playing next track: {self.current_playlist[str(self.current_track_index.value)]['track_name']}")
        self.play_configured_playlist_tracks()
    
    def play_previous(self):
        '''
        Play the previous track in the current playlist
        arguments: None
        returns  : None
        '''
        if not self.current_playlist:
            if self.verbose_mode.value: print("[!] No playlist provided.")
            return

        if self.current_track_index.value <= 0:
            if self.verbose_mode.value: print("[!] Beginning of playlist. Playing the last track.")
            self.current_track_index.value = len(self.current_playlist) - 1
        else:
            self.current_track_index.value -= 1
        if self.verbose_mode.value: print(f"[+] Playing previous track: {self.current_playlist[str(self.current_track_index.value)]['track_name']}")
        self.play_configured_playlist_tracks()
        return
    
    def play_playlist(self, playlist: dict):
        '''
        Play the given playlist
        arguments: playlist: dict {'index' : {'track_name': 'track1', 'file_path': 'path1'}} (JSON object)
        returns  : None
        '''
        if not playlist:
            if self.verbose_mode.value: print("[!] No playlist provided.")
            return

        self.current_playlist = playlist
        self.current_track_index.value = 0
        self.play_configured_playlist_tracks()
        if self.verbose_mode.value: print("[+] Playing the given playlist.")
        return
    
    def set_playlist(self, playlist: dict):
        '''
        Set the given playlist
        arguments: playlist: dict {'index' : {'track_name': 'track1', 'file_path': 'path1'}} (JSON object)
        returns  : None
        '''
        if not playlist:
            if self.verbose_mode.value: print("[!] No playlist provided.")
            return

        self.current_playlist = playlist
        self.current_track_index.value = 0
        if self.verbose_mode.value: print("[+] Playlist set.")
        return

    def play_playlist_from_index(self, index: int):
        '''
        Play the track of given playlist from the given index
        arguments: index: int
        returns  : None
        '''
        if not self.current_playlist:
            if self.verbose_mode.value: print("[!] No playlist configured.")
            return
        if index >= len(self.current_playlist) or index < 0:
            if self.verbose_mode.value: print("[!] Index out of range.")
            return

        self.current_track_index.value = int(index)
        self.play_configured_playlist_tracks()
        return
    
    def stop(self):
        '''
        Stop the current playlist
        arguments: None
        returns  : None
        '''
        if self.current_status_playlist.value:
            self.current_playlist_process.terminate()
            self.current_status_playlist.value = False
            if self.verbose_mode.value: print("[+] Stopped the playlist.")
        elif self.current_status_player.value:
            self.stop_internal_player()
        else:
            if self.verbose_mode.value: print("[!] Nothing playing.")
        if self.verbose_mode.value: print("[+] Bye!")
        return
    
    def wait_for_playlist_end(self):
        '''
        Wait for the current playlist to end
        arguments: None
        returns  : None
        '''
        if self.current_status_playlist.value:
            self.current_playlist_process.join()
            self.current_status_playlist.value = False
            self.stop()
        else:
            if self.verbose_mode.value: print("[!] No playlist playing.")
        return
    
    def set_play_mode(self, mode: str):
        '''
        Set the play mode of the player
        arguments: mode: str (normal, loop, shuffle)
        returns  : None
        '''
        if mode.lower() in ['normal', 'loop', 'shuffle']:
            if mode.lower() == 'normal':
                self.current_play_mode.value = 0
            elif mode.lower() == 'loop':
                self.current_play_mode.value = 1
            elif mode.lower() == 'shuffle':
                self.current_play_mode.value = 2
            if self.verbose_mode.value: print(f"[+] Play mode set to {mode.lower()}.")
        else:
            if self.verbose_mode.value: print("[!] Invalid play mode.")
        return
    
    def get_current_track_name(self):
        return self.current_track_name.value

################################### TEST ####################################
import threading
def wait_and_quit():
    # listen for keyboard 'q' to quit
    print("[!] hit 'q' and press Enter to quit.")
    while True:
        cmd = input()
        if cmd == "q":
            mp3_player.stop()
            break
    return

if __name__ == "__main__":
    banner = """
            ______________  _                         
           (_____________ \| |                        
 ____  ____   ____  _____) ) | ____ _   _  ____  ____ 
|    \|  _ \ (___ \|  ____/| |/ _  | | | |/ _  )/ ___)
| | | | | | |____) ) |     | ( ( | | |_| ( (/ /| |    
|_|_|_| ||_(______/|_|     |_|\_||_|\__  |\____)_|    ~v1.5
      |_|                          (____/             
"""
    print(banner)
    mp3_player = Mp3Player()

    json_file_path = os.path.expanduser('~')+os.sep+'shellify'+os.sep+'playlists'+os.sep+'playlist_1bwbZJ6khPJyVpOaqgKsoZ.json'

    with open(json_file_path, 'r') as f:
        my_playlist = json.load(f)

    mp3_player.play_playlist(my_playlist)
    mp3_player.set_play_mode('loop')

    # mp3_player.play(my_playlist['0'])
    
    print("\n[!] CLI Commands\n n : play next track\n p : play previous track\n q : quit\n")
    while True:
        cmd = input()
        if cmd == "q":
            mp3_player.stop()
            break
        if cmd == "n":
            mp3_player.play_next()
        if cmd == "p":
            mp3_player.play_previous()
    # time.sleep(10)
    # mp3_player.play_previous()
    # time.sleep(10)
    # mp3_player.stop()
    # threading.Thread(target=wait_and_quit).start()