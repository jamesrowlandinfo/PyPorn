PyPorn Media Downloader for Termux
Current Version: 1.5.0
WARNING: This tool is designed for mature audiences and downloads content from various websites, including adult content sites. Use responsibly and in accordance with all applicable laws and terms of service.
PyPorn is a powerful and resilient command-line Python script specifically engineered for users running Termux on Android devices. It provides a robust solution for downloading videos and extracting audio from a wide array of online platforms, including popular sites like YouTube and more challenging ones like Motherless and FetLife. Unlike simpler downloaders, PyPorn is built with advanced workarounds to combat aggressive anti-bot measures, Cloudflare challenges, and site-specific restrictions, ensuring a higher success rate for your media acquisition needs. Whether you're grabbing a single video, an entire playlist, or content from a login-required website, PyPorn aims to simplify the process directly from your Termux terminal.
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
   pkg update -y && pkg upgrade -y

 * Install Python:
   pkg install python

 * Install yt-dlp:
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
   You have a few options to get the script onto your device:
   * Option 1: Using git clone (Recommended for easy updates)
     First, install git if you haven't already:
     pkg install git

     Then, clone the repository:
     git clone https://github.com/jamesrowlandinfo/PyPorn.git

     This will create a PyPorn directory in your current location containing the script.
   * Option 2: Manual Copy-Paste (for single file)
     If you prefer, you can copy the script content directly into a file.
     nano PyPorn.py
# Paste the script content, then Ctrl+X, Y, Enter to save.

     (Note: If you use this method, you'll need to manually update the file for new versions.)
Usage
 * Navigate to the script directory:
   If you used git clone, navigate into the PyPorn directory:
   cd PyPorn

   If you manually saved PyPorn.py in your home directory:
   cd ~/

 * Run the script:
   python PyPorn_1.5.0.py
# Or if you renamed it to PyPorn.py:
# python PyPorn.py

 * Follow the on-screen prompts:
   * Enter the URL of the video or playlist you want to download.
   * Choose your login preference (for sites like FetLife that require authentication).
   * Select whether you want video or audio.
   * If downloading video, choose the desired quality.
   * The downloaded files will be saved to ~/storage/downloads/PyPorn/.
Practical Use Cases
PyPorn is designed to handle various downloading scenarios. Here are some common ways you can use it:
 * Downloading a Single Video:
   Give me the URL of the trash you want to steal (or 'q' to quit, pussy.): https://www.youtube.com/watch?v=dQw4w9WgXcQ
Enter choice (1/2/3): 3  # Continue without login (for public content)
Enter choice (1/2/3): 1
Just pick a damn number for the resolution, any number, you simpleton: 1

   (This will download the best available quality of the single video.)
 * Downloading an Entire YouTube Playlist:
   Give me the URL of the trash you want to steal (or 'q' to quit, pussy.): https://youtube.com/playlist?list=PLIhvC56v63IJ9SYBtdDsNnORfTNFCXR8_
Enter choice (1/2/3): 3  # Continue without login (for public playlist)
Which pieces of garbage do you want? (e.g., '1,3,7'), a range (e.g., '1-5'), 'all' of this bullshit, or 'q' to quit, you fuckin pussy!: all
Enter choice (1/2/3): 1  # For video
Just pick a damn number for the resolution, any number, you simpleton: 1

   (The script will automatically apply delays and throttling between videos to help bypass YouTube's anti-bot measures.)
 * Downloading Specific Videos from a Playlist:
   Give me the URL of the trash you want to steal (or 'q' to quit, pussy.): https://youtube.com/playlist?list=PLIhvC56v63IJ9SYBtdDsNnORfTNFCXR8_
Enter choice (1/2/3): 3  # Continue without login (for public playlist)
Which pieces of garbage do you want? (e.g., '1,3,7'), a range (e.g., '1-5'), 'all' of this bullshit, or 'q' to quit, you fuckin pussy!: 1,5-7,10

   (This will download only videos 1, 5, 6, 7, and 10 from the playlist.)
 * Accessing Content from a Login-Required Site (e.g., FetLife):
   Give me the URL of the trash you want to steal (or 'q' to quit, pussy.): https://fetlife.com/users/your_profile/pictures
Enter choice (1/2/3): 2  # Enter username and password
Enter username: your_username
Enter password: your_password
Enter choice (1/2/3): 1  # For video (if applicable) or 2 for audio

   (Upon successful login, cookies will be saved to ~/storage/downloads/PyPorn/cookies.txt for future use, so you won't need to enter credentials again for that site.)
 * Using a Pre-Existing Cookie File (e.g., exported from a browser):
   Give me the URL of the trash you want to steal (or 'q' to quit, pussy.): https://example.com/private_content
Enter choice (1/2/3): 1  # Use an existing cookie file
Enter path to cookie file (e.g., /data/data/com.termux/files/home/storage/downloads/PyPorn/cookies.txt): /path/to/your/browser_cookies.txt

   (Ensure your cookie file is in the Netscape format, which yt-dlp supports.)
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
