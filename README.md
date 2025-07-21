# PyPorn PyPorn Media Downloader for Termux
WARNING: This tool is designed for mature audiences and downloads content from various websites, including adult content sites. Use responsibly and in accordance with all applicable laws and terms of service.
PyPorn is a command-line Python script built for Termux users, allowing you to download videos and audio from a variety of websites, including YouTube and Motherless. It's designed to be robust against common anti-bot measures and provides options for handling login-required sites.
Features
 * Video Download: Grab videos in the best available quality (or specific resolutions if offered).
 * Audio Extraction: Convert videos to high-quality MP3 audio.
 * Playlist Support: Download entire playlists (with built-in delays and throttling to bypass rate limits).
 * Login & Cookie Handling: Option to use existing cookie files or provide credentials for sites requiring login.
 * Cloudflare Bypass: Includes yt-dlp's impersonate extractor for Cloudflare-protected sites.
 * YouTube Workarounds: Employs multiple YouTube extractors (android, web, web_public, ios) and retries to tackle aggressive anti-bot measures.
 * Resilient Downloads: Retries for failed extractor attempts and download fragments, plus socket timeouts for stability.
 * Automatic Directory Setup: Downloads are saved to ~/storage/downloads/PyPorn/.
 * Interactive CLI: Simple text-based interface for URL input and download options.
 * Debug Mode: Toggleable verbose JSON output for troubleshooting.
Installation (for Termux Users)
Before you can unleash this digital beast, you need to set up your Termux environment.
 * Update Termux Packages:
   pkg update && pkg upgrade -y

 * Install Python:
   pkg install python
   pkg install yt-dlp:
   yt-dlp is the core engine.
   pip install yt-dlp

 * Install ffmpeg:
   Required for audio extraction and combining video/audio streams.
   pkg install ffmpeg

 * Install httpx and h2:
   These are crucial for yt-dlp's Cloudflare bypass capabilities. Without them, you'll hit a wall on many sites.
   pip install httpx h2

 * Grant Storage Permissions:
   This allows Termux to save files to your device's storage.
   termux-setup-storage

   Follow the prompts to grant permission.
 * Download the Script:
   You can either copy the script content directly into a file named PyPorn.py (or PyPorn1.8.py if you prefer to keep versioning) in your Termux home directory, or use wget if you host it somewhere.
   # Example if you copy-paste the content into a file:
nano PyPorn.py
# Paste the script content, then Ctrl+X, Y, Enter to save.

Usage
 * Navigate to the script directory (if not in home):
   cd ~/

   (Assuming you saved it in your home directory)
 * Run the script:
   python PyPorn.py

 * Follow the on-screen prompts:
   * Enter the URL of the video or playlist you want to download.
   * Choose your login preference (for sites like FetLife that require authentication).
   * Select whether you want video or audio.
   * If downloading video, choose the desired quality.
   * The downloaded files will be saved to ~/storage/downloads/PyPorn/.
Important Notes & Troubleshooting
 * HTTP Error 403: Forbidden or Cloudflare anti-bot challenge:
   * This is the most common issue. Ensure httpx and h2 are installed (pip install httpx h2).
   * Always keep yt-dlp updated: pip install --upgrade --force-reinstall yt-dlp. Websites constantly change their defenses.
   * For very stubborn sites (especially YouTube playlists), consider using a VPN or proxy as your IP might be temporarily blocked or rate-limited.
 * DEBUG_MODE: If you encounter issues, ensure DEBUG_MODE = True at the top of the script. This will print the raw JSON output from yt-dlp, which is invaluable for diagnosing problems. Please provide this output if you seek further assistance.
 * Login/Cookies: For sites requiring login, yt-dlp will attempt to use your provided credentials or cookie file. A cookies.txt file will be saved in your PyPorn download directory if you log in, allowing for easier future access.
 * Playlist Delays: For YouTube playlists, a 5-second delay and a 500KB/s throttle are automatically applied between downloads to reduce the chance of being blocked. This means playlist downloads will take longer.
 * Legal Disclaimer: This tool is provided for educational and personal use only. The developer is not responsible for any misuse of this software. Always respect copyright laws and the terms of service of the websites you interact with.
Contributing
Feel free to contribute to this project by opening issues for bugs, suggesting features, or submitting pull requests.
License
This project is open-source and available under the MIT License.



import os
import subprocess
import sys
import json


# --- GLOBAL DEBUG SETTING ---
DEBUG_MODE = True # Set to False to disable verbose JSON output
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
        '--extractor-retries', '3',  # Retry failed extractor attempts up to 3 times
        '--socket-timeout', '10',    # Set socket timeout to 10 seconds
        url
    ]

    if username and password:
        base_command.extend(['--username', username, '--password', password])
    if cookie_file:
        base_command.extend(['--cookies', cookie_file])

    # --- ADVANCED LOGIC FOR YOUTUBE EXTRACTOR HANDLING ---
    if "youtube.com" in url or "youtu.be" in url:
        # List of YouTube player clients to try, from most common to less common.
        # Different clients can sometimes bypass specific YouTube anti-bot measures.
        yt_player_clients_to_try = [
            'youtube',               # Default YouTube extractor
            'youtube:player_client=android', # Android client
            'youtube:player_client=web',     # Web client
            'youtube:player_client=web_public', # Public web client
            'youtube:player_client=ios'      # iOS client
        ]

        for extractor_arg in yt_player_clients_to_try:
            current_command = base_command + ['--extractor-args', extractor_arg]
            try:
                print(f"Attempting with YouTube-DL ({extractor_arg}) extractor...")
                result = subprocess.run(
                    current_command,
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8'
                )
                info = json.loads(result.stdout)
                
                # --- DEBUG OUTPUT ---
                if DEBUG_MODE:
                    print(f"--- DEBUG: Raw info from yt-dlp (Extractor: {extractor_arg}): {json.dumps(info, indent=2)}")
                # --- END DEBUG OUTPUT ---

                return info, None # Success, return info
            except (subprocess.CalledProcessError, json.JSONDecodeError, Exception) as e:
                # If an extractor fails, print the error and try the next one.
                print(f"YouTube-DL ({extractor_arg}) extractor failed: {e}.")
                if extractor_arg == yt_player_clients_to_try[-1]:
                    # If this is the last YouTube-specific extractor, indicate fallback.
                    print("All YouTube-specific extractors failed. Falling back to generic with impersonate...")
                else:
                    print("Trying next YouTube extractor...")
                pass # Continue to the next extractor or fall through


    # Generic command with impersonate (default for non-YouTube or fallback if all YouTube-specific fail)
    # This also includes common retry/timeout args from base_command
    generic_command = base_command + ['--extractor-args', 'generic:impersonate']
    try:
        print("Attempting with generic:impersonate extractor...")
        result = subprocess.run(
            generic_command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        info = json.loads(result.stdout)
        
        # --- DEBUG OUTPUT ---
        if DEBUG_MODE:
            print(f"--- DEBUG: Raw info from yt-dlp (Extractor: generic:impersonate): {json.dumps(info, indent=2)}")
        # --- END DEBUG OUTPUT ---

        return info, None
    except subprocess.CalledProcessError as e:
        return None, f"Error fetching media info. yt-dlp output:\n{e.stderr}"
    except json.JSONDecodeError:
        return None, "Error parsing media info (invalid JSON response from yt-dlp)."
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

    # Iterate through formats to find specific heights (if 'formats' key exists and is not empty)
    # .get('formats', []) ensures this loop doesn't crash if 'formats' key is missing.
    for f in info.get('formats', []): 
        if f.get('vcodec') != 'none' and f.get('height'):
            height = f['height']
            unique_heights.add(height)
    
    # Add specific resolutions found
    for height in sorted(list(unique_heights), reverse=True):
        format_string = f"bestvideo[height={height}]+bestaudio/best[height={height}]"
        options.append((f"{height}p", format_string)) # Display as "720p", "1080p" etc.
    
    # CRITICAL FIX: If the media is identified as a video AND no specific height formats were found,
    # then always add "Best available quality" as a fallback.
    # This handles cases like Motherless where 'formats' might be missing from --dump-json output,
    # but yt-dlp can still download the video using the 'best' format specifier.
    if info.get('_type') == 'video' and not options:
        options.append(("Best available quality", "best")) 
    
    return options


def download_media(url, format_string, output_dir, media_type, playlist_items=None, username=None, password=None, cookie_file=None, save_cookies_to=None):
    """
    Downloads media (video, audio, or images) using yt-dlp.
    It streams yt-dlp's progress directly to the console.
   
    Args:
        url (str): The URL of the media to download.
        format_string (str): The yt-dlp format string (e.g., '247+bestaudio', or specific flags for images/audio).
                             Can be None for audio/image.
        output_dir (str): The directory where the media should be saved.
        media_type (str): 'video', 'audio', or 'image' to determine yt-dlp flags.
        playlist_items (str, optional): A comma-separated string of playlist item numbers (e.g., "1,3,5").
                                        Used with --playlist-items. Defaults to None (all items or single).
        username (str, optional): Username for login. Defaults to None.
        password (str, optional): Password for login. Defaults to None.
        cookie_file (str, optional): Path to a cookie file. Defaults to None.
        save_cookies_to (str, optional): Path to save cookies after successful login. Defaults to None.
    """
    # Define the output file template.
    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
    
    command = ['yt-dlp']
    
    if media_type == 'video':
        command.extend(['-f', format_string])
    elif media_type == 'audio':
        command.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '0'])
        output_template = os.path.join(output_dir, '%(title)s.mp3') # Ensure .mp3 extension
    
    # Add login/cookie flags
    if username and password:
        command.extend(['--username', username, '--password', password])
        if save_cookies_to:
            command.extend(['--write-cookies', save_cookies_to]) # Save cookies after successful login
    elif cookie_file:
        command.extend(['--cookies', cookie_file])

    # Add --playlist-items if specific items are selected
    if playlist_items:
        command.extend(['--playlist-items', playlist_items])
        # Add sleep interval for playlists to avoid rate limiting
        command.extend(['--sleep-interval', '5']) # Sleep 5 seconds between each video in a playlist
        # Add throttled rate for playlists to simulate slower download, can help with anti-bot
        command.extend(['--throttled-rate', '500K']) # Limit to 500 KB/s
        print("\nNOTE: For playlists, a 5-second delay is added between videos and download rate is throttled to 500KB/s to avoid YouTube's anti-bot measures.") # User-interactive dialect
    
    command.extend([
        '-o', output_template,
        '--progress',
        '--extractor-retries', '3',  # Retry failed download attempts up to 3 times
        '--socket-timeout', '10',    # Set socket timeout to 10 seconds
        '--fragment-retries', '10',  # Add fragment retries for broken downloads
        url
    ])

    # Extractor logic for download command, mirroring get_media_info's primary attempt
    if "youtube.com" in url or "youtu.be" in url:
        # Use the 'android' client for download by default for YouTube, as it's often robust.
        # If this fails, the user will see the error and we can adjust.
        command.extend(['--extractor-args', 'youtube:player_client=android'])
    else:
        command.extend(['--extractor-args', 'generic:impersonate']) # Use impersonate for others


    try:
        print(f"\nAlright, you pathetic excuse for a human, I'm trying to download this {media_type} from: {url}") # User-interactive dialect
        if playlist_items:
            print(f"  You picked these specific pieces of shit: {playlist_items}") # User-interactive dialect
            print("  WARNING: YouTube playlists can be difficult to download due to aggressive anti-bot measures. If this fails, try individual videos.") # User-interactive dialect
        print(f"Saving this garbage to: {output_dir}") # User-interactive dialect
       
        process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr)
        process.wait()
       
        if process.returncode == 0:
            print(f"\n{media_type.capitalize()} download complete! Don't thank me, you worthless sack of shit.") # User-interactive dialect
        else:
            print(f"\nError during {media_type} download. yt-dlp choked with code {process.returncode}. What did you expect, you imbecile?") # User-interactive dialect
            print("Go check the URL, your internet connection, and ensure dependencies (ffmpeg, httpx, h2) are installed.") # User-interactive dialect
            if username and password:
                print("Also, check your login credentials. You might be a dumbass and typed them wrong.") # User-interactive dialect
           
    except FileNotFoundError:
        print("Error: I can't find 'yt-dlp', you useless piece of trash. Did you even bother to install it?") # User-interactive dialect
        if media_type == 'audio' or media_type == 'video':
            print("And if you're trying to get audio or certain video formats, you probably need 'ffmpeg' too, you moron. Try: pkg install ffmpeg") # User-interactive dialect
    except Exception as e:
        print(f"Oh, look at that! Something fucked up during your {media_type} download: {e}. You probably broke it, retard.") # User-interactive dialect


def parse_selection(selection_str, max_items):
    """
    Parses user input for item selection (e.g., "1,3,5", "1-5", "all", "7").
    Returns a comma-separated string suitable for --playlist-items.
    """
    selection_str = selection_str.strip().lower()
    if selection_str == 'all':
        return None # None means yt-dlp will download all by default
    
    selected_indices = []
    parts = selection_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if not (1 <= start <= end <= max_items):
                    print(f"YOU FUCKING IDIOT! Range '{part}' is either garbage or out of bounds (1-{max_items}). Get your head out of your ass!") # User-interactive dialect
                    continue
                selected_indices.extend(range(start, end + 1))
            except ValueError:
                print(f"ARE YOU BLIND?! The range format '{part}' is completely wrong. Learn to type before you end up dead fuckin with me.") # User-interactive dialect
        else:
            try:
                idx = int(part)
                if not (1 <= idx <= max_items):
                    print(f"HEY DUMBASS! {idx} is out of bounds (1-{max_items}). Pay attention!") # User-interactive dialect
                    continue
                selected_indices.append(idx)
            except ValueError:
                print(f"WHAT THE FUCK IS WRONG WITH YOU?! That's not a valid item number '{part}'. Are you brain damaged?") # User-interactive dialect
    
    if not selected_indices:
        return "" # Return empty string if no valid selections, to indicate nothing to download
    
    # Remove duplicates and sort
    selected_indices = sorted(list(set(selected_indices)))
    return ",".join(map(str, selected_indices))


def main():
    """
    Main function to run the media downloader script.
    Handles user interaction, directory setup, and calling download functions.
    """
    print("PyPorn Media Downloader for Termux - For RETARDED  HORNY PERVERTS") # User-interactive dialect
    print("-------------------------------------------------------") # User-interactive dialect
    print("Prepare to download some digital filth from websites,") # User-interactive dialect
    print("including YouTube, straight to your pathetic Termux device.") # User-interactive dialect
    print("It's all going into ~/storage/downloads/PyPorn/. If that directory doesn't exist, I'll make it, you lazy bastard.") # User-interactive dialect


    if not check_yt_dlp():
        print("\n--- LISTEN UP, DUMBASS ---") # User-interactive dialect
        print("Error: 'yt-dlp' isn't installed or I can't find it in your system's PATH.") # User-interactive dialect
        print("You're too stupid to run this without it. Here's how, pay attention:") # User-interactive dialect
        print("  pkg install yt-dlp") # User-interactive dialect
        print("Then, try running this garbage script again. Don't waste my time.") # User-interactive dialect
        print("-----------------------------------") # User-interactive dialect
        return


    if not check_ffmpeg():
        print("\n--- Hey, retard! ---") # User-interactive dialect
        print("'ffmpeg' isn't installed or I can't find it.") # User-interactive dialect
        print("You'll need this piece of software to rip audio or combine video/audio for some formats retard!") # User-interactive dialect
        print("Go install it: pkg install ffmpeg") # User-interactive dialect
        print("-----------------------------------") # User-interactive dialect
        return
    

    output_base_dir = os.path.expanduser('~/storage/downloads')
    target_dir = os.path.join(output_base_dir, 'PyPorn')


    try:
        os.makedirs(target_dir, exist_ok=True)
        print(f"\nOutput directory confirmed, you dimwit: {target_dir}") # User-interactive dialect
    except OSError as e:
        print(f"ARE YOU KIDDING ME?! Some shit went wrong trying to create directory '{target_dir}': {e}. You probably fucked it up.") # User-interactive dialect
        print("Do you even have Termux storage permissions enabled? You need that shit.") # User-interactive dialect
        print("Go do it now: termux-setup-storage") # User-interactive dialect
        return


    # --- NEW LOGIN/COOKIE HANDLING VARIABLES ---
    user_username = None
    user_password = None
    user_cookie_file = None
    default_cookie_path = os.path.join(target_dir, 'cookies.txt')
    # --- END NEW LOGIN/COOKIE HANDLING VARIABLES ---


    while True: # Main loop for continuous operation
        media_url = input("\nGive me the URL of the trash you want to steal (or 'q' to quit, pussy.): ").strip() # User-interactive dialect
        if media_url.lower() == 'q':
            break # Exit the loop if user quits


        if not media_url:
            print("ARE YOU FUCKING WITH ME?! Give me a real URL, you absolute waste of space, or do I need to just end your life here and now?") # User-interactive dialect
            continue # Go back to start of loop if URL is empty

        # --- NEW LOGIN/COOKIE PROMPT ---
        print("\n--- LOGIN OPTIONS (for sites like FetLife, if needed) ---")
        print("1. Use an existing cookie file (e.g., from a previous login or browser export)")
        print("2. Enter username and password (cookies will be saved to your PyPorn folder for next time)")
        print("3. Continue without login (for public content)")

        login_choice = input("Enter choice (1/2/3): ").strip()

        if login_choice == '1':
            cookie_path_input = input(f"Enter path to cookie file (e.g., {default_cookie_path}): ").strip()
            user_cookie_file = os.path.expanduser(cookie_path_input) if cookie_path_input else default_cookie_path
            print(f"Attempting to use cookies from: {user_cookie_file}")
            user_username = None # Ensure no conflicting credentials
            user_password = None
        elif login_choice == '2':
            user_username = input("Enter username: ").strip()
            user_password = input("Enter password: ").strip()
            print(f"Credentials entered. Cookies will be saved to: {default_cookie_path}")
            user_cookie_file = None # Ensure no conflicting cookie file
        elif login_choice == '3':
            print("Continuing without login.")
            user_username = None
            user_password = None
            user_cookie_file = None
        else:
            print("Invalid login choice. Continuing without login.")
            user_username = None
            user_password = None
            user_cookie_file = None
        # --- END NEW LOGIN/COOKIE PROMPT ---


        print("\nFINE, I'm checking your pathetic link...") # User-interactive dialect
        # Pass login/cookie info to get_media_info
        info, error_message = get_media_info(media_url, username=user_username, password=user_password, cookie_file=user_cookie_file)

        # --- DEBUG OUTPUT IS NOW HANDLED INSIDE get_media_info FUNCTION ---

        if error_message:
            print(f"OH, FOR FUCK'S SAKE! Your request failed: {error_message}. You probably gave me a broken link, you idiot. I'll fuckin kill you for playing games with me, be careful.") # User-interactive dialect
            print("\n--- IMPORTANT, PAY ATTENTION ---") # User-interactive dialect
            print("If you're getting Cloudflare anti-bot errors, make sure you've installed 'httpx' and 'h2'.") # User-interactive dialect
            print("In Termux, run: pip install httpx h2. Don't come crying to me if you're too dumb to do it.") # User-interactive dialect
            if user_username and user_password:
                print("Also, check your login credentials. You might be a dumbass and typed them wrong.") # User-interactive dialect
            print("----------------------------------") # User-interactive dialect
            continue # Go back to start of loop on error
        
        if not info:
            print("I CAN'T FIND THAT SHIT! Did you even bother to check if it's a real URL? I swear to God I'll cut your throat wide open for playing games with me.") # User-interactive dialect
            continue # Go back to start of loop if no info


        # Determine if it's a playlist/multi-entry URL
        is_multi_item = info.get('_type') == 'playlist' or (info.get('entries') and len(info['entries']) > 1)
        
        selected_playlist_items = None # Initialize here for scope, will be updated if multi-item

        if is_multi_item:
            entries = info.get('entries')
            if not entries: # Handle case where _type is playlist but entries is empty/missing
                print("DAMN IT! This was supposed to be a playlist, but it's empty! What kind of garbage URL did you give me?! Try a different one.") # User-interactive dialect
                continue # Go back to main URL prompt


            print(f"\nLOOK AT ALL THIS SHIT I FOUND ({len(entries)} items):") # User-interactive dialect
            for i, entry in enumerate(entries):
                title = entry.get('title', f"Item {i+1} (No Title, just like your life)")
                print(f"{i + 1}. {title}") # User-interactive dialect
            
            while True:
                selection_input = input(
                    "Which pieces of garbage do you want? (e.g., '1,3,7'), a range (e.g., '1-5'), 'all' of this bullshit, or 'q' to quit, you fuckin pussy!: " # User-interactive dialect
                ).strip()
                
                if selection_input.lower() == 'q':
                    print("FINE! RUN AWAY, YOU COWARD! I QUIT!") # User-interactive dialect
                    break # Break out of selection loop and go back to main URL prompt


                selected_playlist_items = parse_selection(selection_input, len(entries))
                if selected_playlist_items is not None and selected_playlist_items != "":
                    print(f"Alright, you picky bastard, I'll get these specific items: {selected_playlist_items}. Don't fuck it up.") # User-interactive dialect
                    break # Valid selection, break out of selection loop
                elif selected_playlist_items == "":
                    print("ARE YOU SERIOUS?! You have to pick AT LEAST ONE. Try harder loser!") # User-interactive dialect
                elif selection_input.lower() == 'all':
                    print("Fine, I'll download all of this digital trash. Happy now, you greedy pig?") # User-interactive dialect
                    break


            if selection_input.lower() == 'q':
                continue # Go back to main URL prompt if selection was cancelled


        print("\nWHAT KIND OF FILTH DO YOU WANT TO STEAL?:") # User-interactive dialect
        print("1. Video (MP4) - For your pathetic viewing pleasure") # User-interactive dialect
        print("2. Audio (MP3) - So you can listen to this garbage anywhere") # User-interactive dialect
        # Removed option 3 for Images
        # print("3. Thumbnails/Images - Just the tiny pictures, you pervert") 
        
        download_type_choice = input("Enter the number for your desired type, if you can even manage that: ").strip() # User-interactive dialect


        if download_type_choice == '1': # Video
            options = get_available_video_formats(info)


            if not options:
                # This message will now be less frequent due to "Best available quality" fallback
                print("THERE ARE NO VIDEO FORMATS AVAILABLE, YOU IDIOT! It's probably some bullshit that sucks and you're the only one that likes it.. go home to cry and put sand in your vagina while you complain about your extra shy clit and eat ice cream.") # User-interactive dialect
                print("Don't blame me, blame your terrible taste.") # User-interactive dialect
                continue


            print("\nPICK YOUR POISON, YOU DEGENERATE:") # User-interactive dialect
            for i, (display_name, _) in enumerate(options): # Use display_name here
                print(f"{i + 1}. {display_name}") # User-interactive dialect


            while True:
                try:
                    choice_str = input("Just pick a damn number for the resolution, any number, you simpleton: ").strip() # User-interactive dialect
                    if not choice_str:
                        print("YOU HAVE TO PICK ONE, YOU MORON!") # User-interactive dialect
                        continue
                   
                    choice = int(choice_str)
                    if 1 <= choice <= len(options):
                        selected_display_name, selected_format_string = options[choice - 1] # Get both
                        break
                    else:
                        print("ARE YOU FUCKING KIDDING ME?! I GAVE YOU A LIST! PICK A NUMBER FROM THE LIST, DUMBASS!") # User-interactive dialect
                except ValueError:
                    print("CAN YOU EVEN READ?! THAT'S NOT A NUMBER! PICK A NUMBER FROM THE LIST, YOU FUCKIN RETARD!") # User-interactive dialect
           
            download_media(media_url, selected_format_string, target_dir, 'video', selected_playlist_items,
                           username=user_username, password=user_password, cookie_file=user_cookie_file,
                           save_cookies_to=default_cookie_path if user_username else None) # Pass login/cookie info
        
        elif download_type_choice == '2': # Audio
            download_media(media_url, None, target_dir, 'audio', selected_playlist_items,
                           username=user_username, password=user_password, cookie_file=user_cookie_file,
                           save_cookies_to=default_cookie_path if user_username else None) # Pass login/cookie info
        
        # Removed image download option handler
        # elif download_type_choice == '3': # Images
        #     download_media(media_url, None, target_dir, 'image', selected_playlist_items,
        #                    username=user_username, password=user_password, cookie_file=user_cookie_file,
        #                    save_cookies_to=default_cookie_path if user_username else None)


        else:
            print("WHAT THE FUCK IS WRONG WITH YOU?! YOU CAN'T EVEN READ '1', '2', OR '3'?! THOSE ARE YOUR ONLY OPTIONS, YOU RETARD!") # User-interactive dialect
            continue


        print("\n-------------------------------------------------------") # User-interactive dialect


    print("\nExiting PyPorn Media Downloader. Now, GO FUCK YOURSELF AND DON'T COME BACK!") # User-interactive dialect


if __name__ == '__main__':
    main()

