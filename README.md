# Shellify

Shellify is a terminal-based application that allows you to download and play Spotify playlists and albums directly from your terminal. It uses various Python modules to fetch songs from Spotify, download their audio from YouTube, and play them using a built-in MP3 player. Shellify lets you enjoy spotify, without the need of the spotify app and helps you have peace of mind while listening to your favorite songs without annoying ad breaks.

## Features

- Download songs from Spotify playlists and albums
- Play downloaded songs directly from the terminal
- Save playlists as JSON files
- Metadata handling for downloaded MP3 files
- Basic MP3 player functionality (play, next, previous, different play modes)

## Requirements

- Python 3.x
- Spotipy
- Eyed3
- Pytube
- Requests
- FFMPEG
- dotenv
- argparse
- pygame

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/shellify.git
   cd shellify
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Install FFMPEG:

   - For Windows: Download the installer from [FFMPEG official site](https://ffmpeg.org/download.html). Check here for [installation instructions](https://www.wikihow.com/Install-FFmpeg-on-Windows).
   - For MacOS:
     ```bash
     brew install ffmpeg
     ```
   - For Linux:
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```

4. Set up your Spotify API credentials:
   - Create a `.env` file in the project directory with the following content:
     ```env
     CLIENT_ID=your_spotify_client_id
     CLIENT_SECRET=your_spotify_client_secret
     USER_ID=your_spotify_user_id
     ```

## Usage

1. Run the Shellify script with a Spotify playlist or album URL:

   ```bash
   python shellify.py -u <spotify_playlist_or_album_url>
   ```

   Use -h/--help for more information

2. The program will start downloading the songs and playing the first track automatically. Subsequent tracks will be downloaded in the background.

3. Control the playback using the following commands:
   - `n`: Play the next track
   - `p`: Play the previous track
   - `q`: Quit the player

## Project Structure

```plaintext
shellify/
├── modules/
│   ├── sp_downloader.py
│   ├── mp3_player.py
│   └── mini_cli_animator.py
├── shellify.py
├── requirements.txt
├── .env.example
└── README.md
```

### Modules

#### `sp_downloader.py`

This module handles the following:

- Fetching songs from Spotify playlists and albums
- Fetching songs from saved playlist JSONs
- Downloading audio from YouTube
- Converting downloaded audio to MP3 format
- Adding metadata to MP3 files

#### `mp3_player.py`

This module handles the MP3 player functionality:

- Playing MP3 files
- Handling playback controls (play, next, previous, play modes)

#### `mini_cli_animator.py`

This module can be used to add CLI animations and improve user experience. This still work in progress. mp3_player.py uses this module to display a simple animation while playing songs.

## Contributing

Feel free to fork this repository and submit pull requests for any improvements or additional features. If you encounter any issues, please open an issue on the repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Spotipy](https://spotipy.readthedocs.io/) - A light weight Python library for the Spotify Web API
- [Eyed3](https://eyed3.readthedocs.io/) - A Python tool for working with audio files, specifically mp3 files
- [Pytube](https://pytube.io/en/latest/) - A lightweight, dependency-free Python library (and command-line utility) for downloading YouTube videos
- [FFMPEG](https://ffmpeg.org/) - A complete, cross-platform solution to record, convert and stream audio and video
- [Pygame](https://www.pygame.org/) - A set of Python modules designed for writing video games

Enjoy using Shellify!
