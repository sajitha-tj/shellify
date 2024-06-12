import os
import re
import sys
from dotenv import load_dotenv
import argparse
import random
import json
import time
from modules.sp_downloader import Sp_downloader
from modules.mp3_player import Mp3Player
from modules.mini_cli_animator import Mini_cli_animator
import threading


def get_playlist_from_url(playlist_url:str, spd: Sp_downloader):
    # download the playlist from spotify
    print("[+] Getting Songs from spotify")
    # url validation and download
    if "open.spotify.com" not in playlist_url:
        print("[!] Invalid URL. Please provide a valid spotify playlist or album URL.")
        sys.exit(1)
    if "playlist" in playlist_url:
        my_playlist = spd.get_playlist_songs_from_spotify(playlist_url)
    elif "album" in playlist_url:
        my_playlist = spd.get_playlist_from_spotify_album(playlist_url)
    else:
        print("[!] Invalid URL.")
        sys.exit(1)
    return my_playlist

def seperate_downloader(playlist:dict, no_of_threads:int=3):
    print("[+] Downloading songs in background")
    print("[+] No of threads downloading:",no_of_threads)
    threads = []
    for idx in playlist:
        if len(threads) < no_of_threads:
            t = threading.Thread(target=spd.get_id_and_download_single_song, args=(playlist[idx],))
            threads.append(t)
            t.start()
        else:
            for t in threads:
                t.join()
            threads = []
    for t in threads:
        t.join()
    return

def list_playlist_names(spd: Sp_downloader):
    # list all the downloaded playlists
    print("[+] All the downloaded playlists:")
    list_of_playlists = spd.get_list_of_playlists()
    for idx, playlist in enumerate(list_of_playlists):
        print(f"    [{idx+1}] {playlist}")

def list_all_playlists(spd: Sp_downloader):
    # list all the downloaded playlists with songs
    print("[+] All the downloaded playlists with songs:")
    list_of_playlists = spd.get_list_of_playlists()
    for idx, playlist_name in enumerate(list_of_playlists):
        print(f"    [{idx+1}] {playlist_name}")
        temp_playlist = spd.load_playlist_from_json(playlist_name)
        if len(temp_playlist) != 0:
            for idx in temp_playlist:
                print(f"     ├─[{(int(idx)+1)}] {temp_playlist[idx]['track_name']}")

def cli_display(mp3Player: Mp3Player, animater: Mini_cli_animator, playlist):
    # animation thread
    time.sleep(1)
    bar_heights = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    # animater.animate_on_own()
    while True:
        # bars = [random.choice(bar_heights) for _ in range(30)]
        # final_string = ''.join(bars)
        index = mp3Player.current_track_index.value
        track_name = playlist[str(index)]['track_name'].split('(')[0]
        print("[▸] ", track_name) # name
        # print(final_string) # shapes
        animater.animate()
        # print(":", end='') # input line
        time.sleep(0.3)
        print(f"\033[A{' '*0}\033[A{' '*0}", end='\r')


if __name__ == "__main__":
    banner = """
 ______  __  __  ______  __      __      __  ______ __  __    
/\  ___\/\ \_\ \/\  ___\/\ \    /\ \    /\ \/\  ___/\ \_\ \   
\ \___  \ \  __ \ \  __\  \ \___\ \ \___\ \ \ \  __\ \____ \  
 \/\_____\ \_\ \_\ \_____\ \_____\ \_____\ \_\ \_\  \/\_____\ 
  \/_____/\/_/\/_/\/_____/\/_____/\/_____/\/_/\/_/   \/_____/ ~v1.0
"""
    print(banner)

    # load environment variables
    load_dotenv()
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    user_id = os.getenv('USER_ID')

    # argument parser
    usage_msg = "Shellify is a terminal-based application that allows you to download and play Spotify playlists and albums directly from your terminal. Shellify lets you enjoy spotify, without the need of the spotify app and helps you have peace of mind while listening to your favorite songs without annoying ad breaks."
    parser = argparse.ArgumentParser(description=usage_msg)
    parser.add_argument('-u', '--url', type=str, help="Spotify playlist or album URL")
    parser.add_argument('-p', '--playlist', type=str, help="downloaded playlist name")
    parser.add_argument('--list', action='store_true', help="List all the downloaded playlist names")
    parser.add_argument('--list-all', action='store_true', help="List downloaded playlists with songs")
    parser.add_argument('-t', '--threads', type=int, help="No of threads to download songs", default=3)
    parser.add_argument('--no-play', action='store_true', help="Do not play the playlist")
    parser.add_argument('-m', '--mode', type=str, help="Play mode: loop, shuffle, repeat", default="loop", choices=["loop", "shuffle", "repeat"])
    parser.add_argument('-o', '--output', type=str, help="Output file name for the playlist. Can also be used to rename the playlist.")
    args = parser.parse_args()

    # arguments
    playlist_url = args.url
    no_of_threads = args.threads
    playlist_name = args.playlist
    list_playlists_bool = args.list
    list_all_playlists_bool = args.list_all
    is_no_play = args.no_play
    play_mode = args.mode
    output_name = args.output

    # make shellify directory
    dir_path = os.path.expanduser('~')+os.sep+'shellify'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    print("[+] dir_path:",dir_path)

    spd = Sp_downloader(client_id, client_secret, user_id, dir_path, verbose_mode=False)

    # argument handling
    if list_playlists_bool:
        list_playlist_names(spd)
        sys.exit(0)
    elif list_all_playlists_bool:
        list_all_playlists(spd)
        sys.exit(0)
    if playlist_url:
        my_playlist = get_playlist_from_url(playlist_url, spd)
        # save the playlist to a json file
        if output_name:
            spd.save_playlist_to_json(my_playlist, output_name)
            print(f"Playlist saved as '{output_name}'")
        else:
            playlist_id = playlist_url.split('/')[-1].split('?')[0]
            spd.save_playlist_to_json(my_playlist, "playlist_"+playlist_id)
            print(f"[+] Playlist saved as 'playlist_{playlist_id}'")
    elif playlist_name:
        my_playlist = spd.load_playlist_from_json(playlist_name)
        if output_name:
            spd.rename_playlist(playlist_name, output_name)
            print(f"[+] Playlist renamed to {output_name}")

    
    if (my_playlist == None) or (len(my_playlist) <= 0):
        print("[!] Error in playlist")
        sys.exit(1)
          
    # download first track of playlist
    if (spd.check_if_song_exists(my_playlist["0"]) == False):
        print("[+] Downloading first track")
        spd.get_id_and_download_single_song(my_playlist["0"])

    # get id & download the songs, one at once, in background
    threading.Thread(target=seperate_downloader, args=(my_playlist,no_of_threads)).start() #########

    if not is_no_play:
        print("[+] Starting mp3 player")
        mp3Player = Mp3Player(verbose_mode=False)
        animater = Mini_cli_animator()
        mp3Player.play_playlist(my_playlist)
        mp3Player.set_play_mode(play_mode)
        print("[+] Play mode:", play_mode)

        # animation thread
        threading.Thread(target=cli_display, args=(mp3Player,animater, my_playlist,), daemon=True).start()        

        print("\n[!] CLI Commands\n n : play next track\n p : play previous track\n q : quit\n")
        while True:
            cmd = input()
            if cmd == "q":
                mp3Player.stop()
                print("[+] Bye!")
                break
            elif cmd == "n":
                print(f"\033[A \033[A\033[A{' '*35}\n")
                mp3Player.play_next()
            elif cmd == "p":
                print(f"\033[A \033[A\033[A{' '*35}\n")
                mp3Player.play_previous()
            else:
                print(f"\033[A \033[A\033[A{' '*35}\n")