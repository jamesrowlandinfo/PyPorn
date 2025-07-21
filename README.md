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
