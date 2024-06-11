import os
import subprocess
import requests
import spotipy
import eyed3
import json
import re
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
import json
      

class Sp_downloader:

    def __init__(self, client_id="", client_secret="", user_id="", dir_path="", verbose_mode=True):

        self.client_id = client_id
        self.client_secret = client_secret
        self.user_id = user_id
        self.dir_path = dir_path
        self.verbose_mode = verbose_mode
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

        # Initialize SpotiPy with user credentias
        self.auth_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def add_paths_to_playlist_dict(self, my_playlist: dict):
        '''
        Add the file paths to the playlist dictionary
        arguments: playlist: dict
        returns  : playlist: dict
        '''
        dir_path_mp3 = self.dir_path+os.sep+'mp3s'
        if not os.path.exists(dir_path_mp3):
            os.makedirs(dir_path_mp3)

        temp_playlist = my_playlist
        for idx in temp_playlist:
            track_name = temp_playlist[idx]['track_name']
            new_file_name = track_name.replace(" ", "_") # rename with underscores instead of spaces to work with playsound
            # processing file name
            new_file_name = re.sub(r"[^a-zA-Z0-9_]", "", new_file_name)
            temp_playlist[idx]['file_path'] = f"{dir_path_mp3}/{new_file_name}.mp3"
        return temp_playlist

    def get_playlist_songs_from_spotify(self, playlist_url: str):
        '''
        Get the songs in the playlist from spotify
        arguments: playlist_url: str
        returns  : playlist: dict
        '''
        if self.verbose_mode: print("[+] Getting songs from Spotify...")
        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        results = self.sp.playlist_tracks(playlist_id)
        # temp_playlist is a dictionary with index as key and song details as value
        temp_playlist = {}

        for idx, item in enumerate(results['items']):
            track = item['track']
            # getting all artists names
            artist_name = track['artists'][0]['name']
            for i in range(1, len(track['artists'])):
                artist_name += f", {track['artists'][i]['name']}"

            # save song details with index as key. index is integer
            temp_playlist[str(idx)] = {
                'track_name': track['name'],
                'artist_name': artist_name,
                'album_name': track['album']['name']
            }
        
        temp_playlist = self.add_paths_to_playlist_dict(temp_playlist)
        if self.verbose_mode: print("[+] Songs list fetched successfully.")
        if self.verbose_mode: print(f"[+] found {len(temp_playlist)} songs in the playlist.")
        
        return temp_playlist
    
    def get_playlist_from_spotify_album(self, album_url: str):
        '''
        Get the songs in the album from spotify
        arguments: album_url: str
        returns  : playlist: dict
        '''
        if self.verbose_mode: print("[+] Getting songs from Spotify...")
        album_id = album_url.split('/')[-1].split('?')[0]
        results = self.sp.album_tracks(album_id)
        # temp_playlist is a dictionary with index as key and song details as value
        temp_playlist = {}
        album_name = self.sp.album(album_id)['name']

        for idx, item in enumerate(results['items']):
            track = item
            # getting all artists names
            artist_name = track['artists'][0]['name']
            for i in range(1, len(track['artists'])):
                artist_name += f", {track['artists'][i]['name']}"
            
            temp_playlist[str(idx)] = {
                'track_name': track['name'],
                'artist_name': artist_name,
                'album_name': album_name
            }

        temp_playlist = self.add_paths_to_playlist_dict(temp_playlist)
        if self.verbose_mode: print("[+] Songs list fetched successfully.")
        if self.verbose_mode: print(f"[+] found {len(temp_playlist)} songs in the album.")
        
        return temp_playlist
    
    def check_if_song_exists(self, song: dict):
        """
        Check if the song already exists in the directory
        arguments: song: dict
        returns  : None
        """
        track_name = song['track_name']
        file_path = song['file_path']
        # file check for already downloaded songs
        if os.path.exists(f"{file_path}"):
            if self.verbose_mode: print(f"[!] {track_name} already exists.")
            return True
        return False
        

    def get_video_id(self, track_name: str, artist_name: str):
        '''
        Get the youtube video id of the given song, by searching on youtube and getting the first result
        arguments: track_name: str, artist_name: str
        returns  : video_id: str
        '''
        query = f"{track_name} by {artist_name}"
        search_result = requests.get(f"https://www.youtube.com/results?search_query={query}")
        video_id = search_result.text.split('watch?v=')[1].split('"')[0].split('\\')[0]
        if self.verbose_mode: print(f"[+] id for {track_name} : {video_id}")
        return video_id
    
    def get_single_video_id(self, song:dict ):
        '''
        Get the youtube video id of the given song
        arguments: song: dict
        returns  : song: dict
        '''
        temp_song = song
        track_name = temp_song['track_name']
        artist_name = temp_song['artist_name']
        if self.verbose_mode: print(f"[+] Getting youtube video id of {track_name}...")
        song['video_id'] = self.get_video_id(track_name, artist_name)
        if self.verbose_mode: print(f"[+] Youtube video id for {track_name} fetched.")
        return temp_song
        

    def get_alll_youtube_video_ids(self, my_playlist):
        '''
        Get the youtube video ids of the given songs list
        arguments: playlist : dict
        returns : playlist : dict
        '''
        temp_playlist = my_playlist
        if self.verbose_mode: print("[+] Getting youtube video ids...")
        for idx in temp_playlist:
            track_name = temp_playlist[idx]['track_name']
            artist_name = temp_playlist[idx]['artist_name']
            temp_playlist[idx]['video_id'] = self.get_video_id(track_name, artist_name)
        if self.verbose_mode: print("[+] Youtube video ids fetched successfully.")
        return temp_playlist

    def convert_to_mp3(self, old_file_path: str, new_file_path: str):
        '''
        Convert the given file to mp3 format
        arguments: old_file_path: str, new_file_path: str (without extension)
        returns  : new_file_path: str
        '''
        if self.verbose_mode: print(f"[+] Converting {old_file_path} to mp3...")
        subprocess.run(['ffmpeg', '-loglevel', 'quiet' ,'-i', f"{old_file_path}", f"{new_file_path}"], shell=True)
        os.remove(old_file_path)
        if self.verbose_mode: print(f"[+] {old_file_path} converted to mp3 successfully.")
        return new_file_path

    def add_metadata_to_mp3(self, file_path: str, metadata: dict):
        '''
        Add metadata to the given mp3 file
        arguments: file_path: str, metadata: dict
        returns  : None
        '''
        audiofile = eyed3.load(file_path)
        if audiofile.tag == None:
            audiofile.initTag()
        # Add basic tags
        audiofile.tag.title = metadata["track_name"]
        audiofile.tag.album = metadata["album_name"]
        audiofile.tag.artist = metadata["artist_name"]
        audiofile.tag.save()
        if self.verbose_mode: print(f"[+] Metadata added to {file_path} successfully.")

    def download_audio_from_youtube(self, song: dict):
        '''
        Download the audio from youtube video (single song)
        arguments: song: dict
        returns  : file_path: str
        '''
        video_id = song['video_id']
        track_name = song['track_name']
        new_file_name = song['file_path']

        dir_path_mp3s = self.dir_path+os.sep+'mp3s'
        if not os.path.exists(dir_path_mp3s):
            os.makedirs(dir_path_mp3s)

        # file check for already downloaded songs
        if self.check_if_song_exists(song):
            return new_file_name
        
        # download the audio (mp4)
        if self.verbose_mode: print(f"[+] Downloading tack: {track_name}")
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        out_path = yt.streams.filter(only_audio=True).first().download(dir_path_mp3s)
        if self.verbose_mode: print(f"[+] {track_name} downloaded successfully.")
        
        # convert to mp3 and add metadata
        mp3_path = self.convert_to_mp3(out_path, f"{new_file_name}")
        self.add_metadata_to_mp3(mp3_path, song)
        return mp3_path
    
    def get_id_and_download_single_song(self, song: dict):
        '''
        Get the youtube video id of the given song and download the audio
        arguments: song: dict
        returns  : file_path: str
        '''
        temp_song = song
        temp_song = self.get_single_video_id(temp_song)
        if self.check_if_song_exists(temp_song):
            return temp_song['file_path']
        file_path = self.download_audio_from_youtube(temp_song)
        return file_path
    
    def save_playlist_to_json(self, playlist: dict, name: str):
        '''
        Save the playlist to a json file
        arguments: playlist: dict, name: str
        returns  : None
        '''
        dir_path_playlist = self.dir_path+os.sep+'playlists'
        if not os.path.exists(dir_path_playlist):
            os.makedirs(dir_path_playlist)

        if name == "":
            name = "playlist"

        name = name.replace(" ", "_").replace("-", "_")
        name = re.sub(r"[^a-zA-Z0-9_]", "", name)

        file_to_save = f"{dir_path_playlist}/{name}.json"
        # overwrite the file if it already exists
        with open(file_to_save, 'w') as f:
            json.dump(playlist, f)
        if self.verbose_mode: print(f"[+] Playlist saved to {file_to_save} successfully.")
        return
    
    def rename_playlist(self, old_name: str, new_name: str):
        '''
        Rename the playlist
        arguments: old_name: str, new_name: str
        returns  : None
        '''
        new_name = new_name.replace(" ", "_").replace("-", "_")
        new_name = re.sub(r"[^a-zA-Z0-9_]", "", new_name)
        if not old_name.endswith('.json') and not old_name.isdecimal():
            old_name = old_name + '.json'
        if not os.path.exists(old_name):
            if os.path.exists(self.dir_path+os.sep+'playlists'+os.sep+old_name):
                old_name = self.dir_path+os.sep+'playlists'+os.sep+old_name
            else:
                if (old_name.isdecimal()):
                    playlists = self.get_list_of_playlists()
                    if (int(old_name) <= len(playlists)) and (int(old_name) > 0):
                        old_name = playlists[int(old_name)-1]
                        old_name = self.dir_path+os.sep+'playlists'+os.sep+old_name
                    else:
                        print("[!] index out of range!")
                        return None
                else:
                    print("[!] Playlist not found.")
                    return None
        new_name = self.dir_path + os.sep + 'playlists' + os.sep + new_name + '.json'
        os.rename(f"{old_name}", f"{new_name}")
        if self.verbose_mode: print(f"[+] Playlist renamed to {new_name} successfully.")
        return
    
    def get_list_of_playlists(self):
        '''
        List all the downloaded playlists
        arguments: None
        returns  : list of playlists
        '''
        dir_path_playlist = self.dir_path+os.sep+'playlists'
        if not os.path.exists(dir_path_playlist):
            if self.verbose_mode: print("[!] No playlists found.")
            return None
        return os.listdir(dir_path_playlist)
    
    def load_playlist_from_json(self, playlist_name: str):
        '''
        Load the playlist from a json file
        arguments: name: str
        returns  : playlist: dict
        '''
        if not playlist_name.endswith('.json') and not playlist_name.isdecimal():
            playlist_name = playlist_name + '.json'
        if not os.path.exists(playlist_name):
            if os.path.exists(self.dir_path+os.sep+'playlists'+os.sep+playlist_name):
                playlist_name = self.dir_path+os.sep+'playlists'+os.sep+playlist_name
            else:
                if (playlist_name.isdecimal()):
                    playlists = self.get_list_of_playlists()
                    if (int(playlist_name) <= len(playlists)) and (int(playlist_name) > 0):
                        playlist_name = playlists[int(playlist_name)-1]
                        playlist_name = self.dir_path+os.sep+'playlists'+os.sep+playlist_name
                    else:
                        print("[!] index out of range!")
                        return None
                else:
                    print("[!] Playlist not found.")
                    return None
        if self.verbose_mode: print("[+] Loading playlist from json file")
        with open(playlist_name, 'r') as f:
            my_playlist = json.load(f)
        return my_playlist
    
    


###############################################
##                  MAIN                     ##
###############################################

# if __name__ == "__main__":
#     # Get the playlist url from arguments
#     if len(sys.argv) < 2:
#         print("Invalid arguments. Please provide the playlist URL.\nUsage: python pl_downloader.py <playlist_url>")
#         sys.exit(1)

#     playlist_url = sys.argv[1]
#     if "open.spotify.com" not in playlist_url:
#         print("Invalid URL. Please provide a valid spotify playlist or album URL.\nUsage: python pl_downloader.py <playlist_url>")
#         sys.exit(1)

#     # load environment variables
#     load_dotenv()
#     client_id = os.getenv('CLIENT_ID')
#     client_secret = os.getenv('CLIENT_SECRET')
#     user_id = os.getenv('USER_ID')

#     # make shellify directory
#     dir_path = os.path.expanduser('~')+os.sep+'sp_downloader'
#     if not os.path.exists(dir_path):
#         os.makedirs(dir_path)
#     print(dir_path)

#     spd = Sp_downloader(client_id, client_secret, user_id, dir_path)

#     # get the songs from spotify
#     if "playlist" in playlist_url:
#         my_playlist = spd.get_playlist_songs_from_spotify(playlist_url)
#     elif "album" in playlist_url:
#         my_playlist = spd.get_playlist_from_spotify_album(playlist_url)
#     else:
#         print("Invalid URL. Please provide a valid spotify playlist or album URL.\nUsage: python pl_downloader.py <playlist_url>")
#         sys.exit(1)

#     # # TEMP #########################################
#     # if (len(sys.argv) == 3) and (sys.argv[2] == "v"):
#     #     if self.verbose_mode: print(my_playlist)
#     #     sys.exit(0)

#     # # cut the playlist to 2 songs
#     # temp_playlist = {}
#     # for idx in range(2):
#     #     temp_playlist[idx] = my_playlist[idx]
#     # my_playlist = temp_playlist
#     # # END TEMP #####################################

#     my_playlist = spd.get_alll_youtube_video_ids(my_playlist) # get the youtube video ids of the songs

#     # download audio files
#     print("[+] Downloading your playlist...")

#     for idx in my_playlist:
#         threading.Thread(target=spd.download_audio_from_youtube, args=(my_playlist[idx],)).start()

#     # save the playlist to a json file
#     playlist_id = playlist_url.split('/')[-1].split('?')[0]
#     spd.save_playlist_to_json(my_playlist, "playlist_"+playlist_id)
