import os
import subprocess
import sys
import json
from pydub import AudioSegment
from pydub.silence import split_on_silence

# --- GLOBAL DEBUG SETTING ---
DEBUG_MODE = True  # Set to False to disable verbose JSON output
# --- END GLOBAL DEBUG SETTING ---

def check_yt_dlp():
    """
    Checks if yt-dlp is installed and executable by trying to get its version.
    Returns True if found, False otherwise.
    """
    try:
        subprocess.run(['yt-dlp', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_ffmpeg():
    """
    Checks if ffmpeg is installed and executable by trying to get its version.
    Returns True if found, False otherwise.
    """
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_pydub():
    """
    Checks if pydub is installed.
    Returns True if found, False otherwise.
    """
    try:
        import pydub
        return True
    except ImportError:
        return False

def get_media_info(url, username=None, password=None, cookie_file=None):
    """
    Fetches and parses detailed media information for a given URL using yt-dlp's JSON output.
    Includes various extractor attempts and common workarounds.
    
    Args:
        url (str): The URL of the media to analyze.
        username (str, optional): Username for login. Defaults to None.
        password (str, optional): Password for login. Defaults to None.
        cookie_file (str, optional): Path to a cookie file. Defaults to None.

    Returns:
        tuple: A tuple containing:
               - dict: The full JSON info dictionary from yt-dlp, or None if an error occurred.
               - str: An error message if an error occurred, otherwise None.
    """
    base_command = [
        'yt-dlp',
        '--dump-json',
        '--no-warnings',
        '--no-simulate',
        '--extractor-retries', '3',
        '--socket-timeout', '10',
        url
    ]

    if username and password:
        base_command.extend(['--username', username, '--password', password])
    if cookie_file:
        base_command.extend(['--cookies', cookie_file])

    if "youtube.com" in url or "youtu.be" in url:
        yt_player_clients_to_try = [
            'youtube',
            'youtube:player_client=android',
            'youtube:player_client=web',
            'youtube:player_client=web_public',
            'youtube:player_client=ios'
        ]

        for extractor_arg in yt_player_clients_to_try:
            current_command = base_command + ['--extractor-args', extractor_arg]
            try:
                print(f"Attempting to fetch media info with {extractor_arg} extractor...")
                result = subprocess.run(
                    current_command,
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                info = json.loads(result.stdout)
                
                if DEBUG_MODE:
                    print(f"--- DEBUG: Raw info from yt-dlp (Extractor: {extractor_arg}): {json.dumps(info, indent=2)}")
                
                return info, None
            except (subprocess.CalledProcessError, json.JSONDecodeError, Exception) as e:
                print(f"Failed with {extractor_arg} extractor: {e}")
                if extractor_arg == yt_player_clients_to_try[-1]:
                    print("All YouTube-specific extractors failed. Falling back to generic extractor...")
                else:
                    print("Trying next YouTube extractor...")
                pass

    generic_command = base_command + ['--extractor-args', 'generic:impersonate']
    try:
        print("Attempting to fetch media info with generic:impersonate extractor...")
        result = subprocess.run(
            generic_command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        info = json.loads(result.stdout)
        
        if DEBUG_MODE:
            print(f"--- DEBUG: Raw info from yt-dlp (Extractor: generic:impersonate): {json.dumps(info, indent=2)}")
        
        return info, None
    except subprocess.CalledProcessError as e:
        return None, f"Error fetching media info: {e.stderr}"
    except json.JSONDecodeError:
        return None, "Error parsing media info: Invalid JSON response from yt-dlp."
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"

def get_available_video_formats(info):
    """
    Extracts and formats available video resolutions from the yt-dlp info dictionary.
    
    Args:
        info (dict): The yt-dlp info dictionary for the media.

    Returns:
        list: A list of tuples (display_name, yt_dlp_format_string) for available options.
              Sorted by height in descending order, with a fallback "Best available" option.
    """
    options = []
    unique_heights = set()

    for f in info.get('formats', []):
        if f.get('vcodec') != 'none' and f.get('height'):
            height = f['height']
            unique_heights.add(height)
    
    for height in sorted(list(unique_heights), reverse=True):
        format_string = f"bestvideo[height={height}]+bestaudio/best[height={height}]"
        options.append((f"{height}p", format_string))
    
    if info.get('_type') == 'video' and not options:
        options.append(("Best available quality", "best"))
    
    return options

def download_media(url, format_string, output_dir, media_type, playlist_items=None, username=None, password=None, cookie_file=None, save_cookies_to=None):
    """
    Downloads media (video or audio) using yt-dlp.
    Streams yt-dlp's progress directly to the console.
   
    Args:
        url (str): The URL of the media to download.
        format_string (str): The yt-dlp format string (e.g., '247+bestaudio', or None for audio).
        output_dir (str): The directory where the media should be saved.
        media_type (str): 'video' or 'audio' to determine yt-dlp flags.
        playlist_items (str, optional): A comma-separated string of playlist item numbers (e.g., "1,3,5").
        username (str, optional): Username for login. Defaults to None.
        password (str, optional): Password for login. Defaults to None.
        cookie_file (str, optional): Path to a cookie file. Defaults to None.
        save_cookies_to (str, optional): Path to save cookies after successful login. Defaults to None.

    Returns:
        list: List of paths to downloaded files, or empty list if download fails.
    """
    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
    downloaded_files = []
    
    command = ['yt-dlp']
    
    if media_type == 'video':
        command.extend(['-f', format_string])
    elif media_type == 'audio':
        command.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '0'])
        output_template = os.path.join(output_dir, '%(title)s.mp3')
    
    if username and password:
        command.extend(['--username', username, '--password', password])
        if save_cookies_to:
            command.extend(['--write-cookies', save_cookies_to])
    elif cookie_file:
        command.extend(['--cookies', cookie_file])

    if playlist_items:
        command.extend(['--playlist-items', playlist_items])
        command.extend(['--sleep-interval', '5'])
        command.extend(['--throttled-rate', '500K'])
        print("\nNote: For playlists, a 5-second delay is added between videos, and the download rate is limited to 500KB/s to help avoid rate-limiting issues.")
    
    command.extend([
        '-o', output_template,
        '--progress',
        '--extractor-retries', '3',
        '--socket-timeout', '10',
        '--fragment-retries', '10',
        url
    ])

    if "youtube.com" in url or "youtu.be" in url:
        command.extend(['--extractor-args', 'youtube:player_client=android'])
    else:
        command.extend(['--extractor-args', 'generic:impersonate'])

    try:
        print(f"\nStarting {media_type} download from: {url}")
        if playlist_items:
            print(f"Selected playlist items: {playlist_items}")
            print("Note: Downloading playlists may encounter issues due to rate-limiting protections. If this fails, consider downloading individual items.")
        print(f"Saving to: {output_dir}")
       
        process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr)
        process.wait()
       
        if process.returncode == 0:
            print(f"\n{media_type.capitalize()} download completed successfully!")
            if media_type == 'audio':
                if playlist_items:
                    for idx in parse_selection(playlist_items, 9999).split(',') if playlist_items else ['']:
                        for f in os.listdir(output_dir):
                            if f.endswith('.mp3') and os.path.isfile(os.path.join(output_dir, f)):
                                downloaded_files.append(os.path.join(output_dir, f))
                else:
                    for f in os.listdir(output_dir):
                        if f.endswith('.mp3') and os.path.isfile(os.path.join(output_dir, f)):
                            downloaded_files.append(os.path.join(output_dir, f))
        else:
            print(f"\nError during {media_type} download. yt-dlp returned error code {process.returncode}.")
            print("Please verify the URL, your internet connection, and ensure dependencies (ffmpeg, httpx, h2) are installed.")
            if username and password:
                print("Additionally, please check your login credentials for accuracy.")
            return []
           
    except FileNotFoundError:
        print("Error: yt-dlp is not installed or not found in your system's PATH.")
        if media_type == 'audio' or media_type == 'video':
            print("For audio or certain video formats, ffmpeg is also required. Install it with: pkg install ffmpeg")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during {media_type} download: {e}")
        return []
    
    return downloaded_files

def split_audio_by_chunk(audio_file, output_dir, chunk_length_ms):
    """
    Splits an audio file into equal chunks of specified length using pydub.
    
    Args:
        audio_file (str): Path to the audio file to split.
        output_dir (str): Directory to save split chunks.
        chunk_length_ms (int): Length of each chunk in milliseconds.
    """
    try:
        print(f"Splitting audio into chunks of {chunk_length_ms / 60000:.1f} minutes...")
        chunk_dir = os.path.join(output_dir, "split_chunks")
        os.makedirs(chunk_dir, exist_ok=True)

        audio = AudioSegment.from_file(audio_file)
        duration_ms = len(audio)
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, duration_ms, chunk_length_ms)]

        for i, chunk in enumerate(chunks):
            chunk_name = os.path.join(chunk_dir, f"{os.path.splitext(os.path.basename(audio_file))[0]}_chunk{i+1}.mp3")
            chunk.export(chunk_name, format="mp3")
            print(f"Saved chunk: {chunk_name}")

        print(f"\nAudio successfully split into {len(chunks)} chunks in: {chunk_dir}")
    except Exception as e:
        print(f"Error splitting audio by chunk length: {e}")

def split_audio_by_silence(audio_file, output_dir, min_silence_len=500, silence_thresh=-40, min_chunk_length_ms=300000):
    """
    Splits an audio file based on silence detection using pydub.
    
    Args:
        audio_file (str): Path to the audio file to split.
        output_dir (str): Directory to save split chunks.
        min_silence_len (int): Minimum length of silence in milliseconds to detect a split.
        silence_thresh (int): Silence threshold in dBFS (e.g., -40 dBFS).
        min_chunk_length_ms (int): Minimum length of chunks in milliseconds (default: 5 minutes).
    """
    try:
        print(f"Splitting audio by silence detection...")
        chunk_dir = os.path.join(output_dir, "split_chunks")
        os.makedirs(chunk_dir, exist_ok=True)

        audio = AudioSegment.from_file(audio_file)
        chunks = split_on_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            keep_silence=200
        )

        filtered_chunks = [chunk for chunk in chunks if len(chunk) >= min_chunk_length_ms]
        if not filtered_chunks:
            print("No chunks meet the minimum length requirement. Try adjusting silence parameters.")
            return

        for i, chunk in enumerate(filtered_chunks):
            chunk_name = os.path.join(chunk_dir, f"{os.path.splitext(os.path.basename(audio_file))[0]}_chunk{i+1}.mp3")
            chunk.export(chunk_name, format="mp3")
            print(f"Saved chunk: {chunk_name}")

        print(f"\nAudio successfully split into {len(filtered_chunks)} chunks in: {chunk_dir}")
    except Exception as e:
        print(f"Error splitting audio by silence: {e}")

def split_audio_by_silence_then_chunks(audio_file, output_dir, chunk_length_ms, min_silence_len=500, silence_thresh=-40):
    """
    Splits an audio file by removing silence, then splits the concatenated non-silent audio into equal chunks.
    
    Args:
        audio_file (str): Path to the audio file to split.
        output_dir (str): Directory to save split chunks.
        chunk_length_ms (int): Length of each chunk in milliseconds after silence removal.
        min_silence_len (int): Minimum length of silence in milliseconds to detect.
        silence_thresh (int): Silence threshold in dBFS (e.g., -40 dBFS).
    """
    try:
        print(f"Removing silence and splitting into chunks of {chunk_length_ms / 60000:.1f} minutes...")
        chunk_dir = os.path.join(output_dir, "split_chunks")
        os.makedirs(chunk_dir, exist_ok=True)

        audio = AudioSegment.from_file(audio_file)
        non_silent_chunks = split_on_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            keep_silence=200
        )

        if not non_silent_chunks:
            print("No non-silent segments detected. Try adjusting silence parameters.")
            return

        concatenated_audio = AudioSegment.empty()
        for chunk in non_silent_chunks:
            concatenated_audio += chunk

        duration_ms = len(concatenated_audio)
        if duration_ms < chunk_length_ms:
            print(f"Error: After removing silence, audio duration ({duration_ms / 1000:.1f}s) is shorter than requested chunk length ({chunk_length_ms / 1000:.1f}s).")
            return

        chunks = [concatenated_audio[i:i + chunk_length_ms] for i in range(0, duration_ms, chunk_length_ms)]

        for i, chunk in enumerate(chunks):
            chunk_name = os.path.join(chunk_dir, f"{os.path.splitext(os.path.basename(audio_file))[0]}_chunk{i+1}.mp3")
            chunk.export(chunk_name, format="mp3")
            print(f"Saved chunk: {chunk_name}")

        print(f"\nAudio successfully split into {len(chunks)} chunks after silence removal in: {chunk_dir}")
    except Exception as e:
        print(f"Error splitting audio by silence then chunks: {e}")

def select_audio_file(output_dir):
    """
    Lists MP3 files in the output directory and allows the user to select one for splitting.
    
    Args:
        output_dir (str): Directory to search for MP3 files.

    Returns:
        str: Path to the selected audio file, or None if no file is selected or available.
    """
    mp3_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3') and os.path.isfile(os.path.join(output_dir, f))]
    if not mp3_files:
        print("No MP3 files found in the output directory.")
        return None

    print("\nAvailable MP3 files:")
    for i, f in enumerate(mp3_files, 1):
        print(f"{i}. {f}")

    while True:
        try:
            choice = input("Select a file number (or 'q' to cancel): ").strip()
            if choice.lower() == 'q':
                return None
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(mp3_files):
                return os.path.join(output_dir, mp3_files[choice_idx])
            else:
                print(f"Error: Please select a number between 1 and {len(mp3_files)}.")
        except ValueError:
            print("Error: Please enter a valid number or 'q' to cancel.")

def parse_selection(selection_str, max_items):
    """
    Parses user input for item selection (e.g., "1,3,5", "1-5", "all", "7").
    Returns a comma-separated string suitable for --playlist-items.
    """
    selection_str = selection_str.strip().lower()
    if selection_str == 'all':
        return None
    
    selected_indices = []
    parts = selection_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if not (1 <= start <= end <= max_items):
                    print(f"Error: Range '{part}' is invalid or out of bounds (1-{max_items}). Please try again.")
                    continue
                selected_indices.extend(range(start, end + 1))
            except ValueError:
                print(f"Error: Invalid range format '{part}'. Please use a format like '1-5'.")
        else:
            try:
                idx = int(part)
                if not (1 <= idx <= max_items):
                    print(f"Error: {idx} is out of bounds (1-{max_items}). Please select a valid item.")
                    continue
                selected_indices.append(idx)
            except ValueError:
                print(f"Error: '{part}' is not a valid item number. Please enter a number or range.")
    
    if not selected_indices:
        return ""
    
    selected_indices = sorted(list(set(selected_indices)))
    return ",".join(map(str, selected_indices))

def main():
    """
    Main function to run the Pyanide media downloader script.
    Handles user interaction, directory setup, and calling download and splitting functions.
    """
    print("Welcome to Pyanide - Media Downloader and Editor for Termux")
    print("---------------------------------------------------------")
    print("This tool allows you to download videos and audio from various websites, including YouTube.")
    print("You can also edit existing audio files by splitting them into chunks based on duration, silence detection, or silence removal followed by equal chunks.")
    print("Downloads and edited files will be saved to ~/storage/downloads/Pyanide/.")

    if not check_yt_dlp():
        print("\n--- Error ---")
        print("yt-dlp is not installed or not found in your system's PATH.")
        print("Please install it by running: pkg install yt-dlp")
        print("Then, try running Pyanide again.")
        return

    if not check_ffmpeg():
        print("\n--- Error ---")
        print("ffmpeg is not installed or not found.")
        print("ffmpeg is required for audio extraction, video formats, and audio splitting.")
        print("Please install it by running: pkg install ffmpeg")
        return
    
    if not check_pydub():
        print("\n--- Error ---")
        print("pydub is not installed.")
        print("pydub is required for audio splitting functionality.")
        print("Please install it by running: pip install pydub")
        return
    
    output_base_dir = os.path.expanduser('~/storage/downloads')
    target_dir = os.path.join(output_base_dir, 'Pyanide')

    try:
        os.makedirs(target_dir, exist_ok=True)
        print(f"\nOutput directory set to: {target_dir}")
    except OSError as e:
        print(f"Error: Could not create directory