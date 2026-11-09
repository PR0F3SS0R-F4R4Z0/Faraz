#!/usr/bin/env python3

"""
╔══════════════════════════════════════════════════════════════╗
║          FARAZO VIDEO DOWNLOADER v5.2 SMART AUTO-FIX        ║
║              ULTRA SPEED + SMART ERROR RECOVERY             ║
╚══════════════════════════════════════════════════════════════╝

FEATURES
────────
✓ yt-dlp powered
✓ FFmpeg detection
✓ FAST / ULTRA download modes
✓ Concurrent fragments
✓ Resume interrupted downloads
✓ Smart retries
✓ Automatic yt-dlp update attempt
✓ Automatic retry after update
✓ Smart error detection
✓ TikTok / YouTube / Facebook error messages
✓ Format scanner
✓ 144p → 4K
✓ MP3
✓ Playlist support
✓ Download archive
✓ Continuous mode

NOTE:
This tool can recover from some extractor/version errors.
It cannot bypass DRM, private permissions, passwords,
paywalls, or other access restrictions.
"""

import os
import sys
import re
import shutil
import subprocess
from pathlib import Path


# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════

DL_DIR = Path("/sdcard/Movies/FARAZO")
ARCHIVE_FILE = DL_DIR / ".farazo_archive.txt"

MAX_RETRIES = "10"
FRAGMENT_RETRIES = "10"
BUFFER_SIZE = "16K"

FFMPEG_PATHS = [
    "/data/data/com.termux/files/usr/bin/ffmpeg",
    "/usr/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
]


# ══════════════════════════════════════════════════════════════
# COLORS
# ══════════════════════════════════════════════════════════════

RESET = "\033[0m"
BOLD = "\033[1m"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GRAY = "\033[90m"


# ══════════════════════════════════════════════════════════════
# QUALITY MAP
# ══════════════════════════════════════════════════════════════

QUALITY_MAP = {

    "1": (
        "♫ AUDIO MP3",
        "bestaudio/best",
        True
    ),

    "2": (
        "▶ 144p",
        "bestvideo[height<=144]+bestaudio/best[height<=144]/best",
        False
    ),

    "3": (
        "▶ 240p",
        "bestvideo[height<=240]+bestaudio/best[height<=240]/best",
        False
    ),

    "4": (
        "▶ 360p",
        "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
        False
    ),

    "5": (
        "▶ 480p",
        "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
        False
    ),

    "6": (
        "▶ 720p HD",
        "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        False
    ),

    "7": (
        "▶ 1080p FHD",
        "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        False
    ),

    "8": (
        "▶ 1440p 2K",
        "bestvideo[height<=1440]+bestaudio/best[height<=1440]/best",
        False
    ),

    "9": (
        "▶ 2160p 4K",
        "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best",
        False
    ),

    "10": (
        "★ BEST AVAILABLE",
        "bestvideo*+bestaudio/best",
        False
    ),

    "11": (
        "★ BEST MP4",
        "bestvideo[vcodec^=avc]+bestaudio[acodec^=mp4a]/best[ext=mp4]/best",
        False
    ),
}


# ══════════════════════════════════════════════════════════════
# TERMINAL FUNCTIONS
# ══════════════════════════════════════════════════════════════

def clear():
    os.system("clear")


def line():
    print(f"{GRAY}{'━' * 62}{RESET}")


def status(label, value, color=GREEN):
    print(
        f"  {GRAY}│{RESET} "
        f"{WHITE}{label:<14}{RESET} "
        f"{color}{value}{RESET}"
    )


def logo():

    print(f"""
{RED}{BOLD}
███████╗ █████╗ ██████╗  █████╗ ███████╗ ██████╗
██╔════╝██╔══██╗██╔══██╗██╔══██╗╚══███╔╝██╔═══██╗
█████╗  ███████║██████╔╝███████║  ███╔╝ ██║   ██║
██╔══╝  ██╔══██║██╔══██╗██╔══██║ ███╔╝  ██║   ██║
██║     ██║  ██║██║  ██║██║  ██║███████╗╚██████╔╝
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝
{RESET}
{CYAN}{BOLD}                    F A R A Z O{RESET}
{GRAY}             SMART AUTO-FIX DOWNLOADER{RESET}
""")


# ══════════════════════════════════════════════════════════════
# PROGRESS
# ══════════════════════════════════════════════════════════════

def progress_bar(percent, width=18):

    try:
        percent = float(percent)
    except:
        percent = 0

    percent = max(0, min(100, percent))

    filled = int(width * percent / 100)

    return (
        f"{GREEN}"
        + "█" * filled
        + f"{GRAY}"
        + "░" * (width - filled)
        + RESET
    )


def show_progress(text):

    percent = "--"
    downloaded = "--"
    total = "--"
    speed = "--"
    eta = "--:--"

    value = 0

    match = re.search(r"(\d+(?:\.\d+)?)%", text)

    if match:

        try:
            value = float(match.group(1))
            percent = f"{value:5.1f}%"
        except:
            pass

    match = re.search(
        r"\[download\]\s+([0-9.]+[A-Za-z]+)\s+of\s+([0-9.]+[A-Za-z]+)",
        text
    )

    if match:
        downloaded = match.group(1)
        total = match.group(2)

    match = re.search(
        r"at\s+(.+?)(?:\s+ETA|$)",
        text
    )

    if match:
        speed = match.group(1).strip()

    match = re.search(
        r"ETA\s+([0-9:]+)",
        text
    )

    if match:
        eta = match.group(1)

    bar = progress_bar(value)

    print(
        f"\r{CYAN}⚡ FARAZO{RESET} │ "
        f"{bar} │ "
        f"{WHITE}{percent}{RESET} │ "
        f"{YELLOW}{downloaded}/{total}{RESET} │ "
        f"{BLUE}{speed}{RESET} │ "
        f"{MAGENTA}ETA {eta}{RESET}",
        end="",
        flush=True
    )


# ══════════════════════════════════════════════════════════════
# SYSTEM
# ══════════════════════════════════════════════════════════════

def find_ffmpeg():

    for path in FFMPEG_PATHS:

        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    return shutil.which("ffmpeg")


def get_ytdlp_version():

    try:

        return subprocess.check_output(
            ["yt-dlp", "--version"],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()

    except:

        return None


def ensure_ytdlp():

    version = get_ytdlp_version()

    if version:
        return version

    print(f"{YELLOW}[!] yt-dlp not found{RESET}")

    try:

        subprocess.run(
            ["pkg", "install", "-y", "yt-dlp"]
        )

    except:
        pass

    return get_ytdlp_version()


# ══════════════════════════════════════════════════════════════
# UPDATE YT-DLP
# ══════════════════════════════════════════════════════════════

def update_ytdlp():

    print()
    print(
        f"{CYAN}  ⚡ SMART UPDATE STARTED...{RESET}"
    )

    old_version = get_ytdlp_version()

    commands = [

        ["yt-dlp", "-U"],

        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "yt-dlp"
        ],
    ]

    for command in commands:

        try:

            result = subprocess.run(
                command
            )

            if result.returncode == 0:

                new_version = get_ytdlp_version()

                print()

                print(
                    f"{GREEN}"
                    f"  ✓ yt-dlp: {old_version} → {new_version}"
                    f"{RESET}"
                )

                return True

        except:
            pass

    print(
        f"{RED}"
        "  ✖ AUTO UPDATE FAILED"
        f"{RESET}"
    )

    return False


# ══════════════════════════════════════════════════════════════
# URL
# ══════════════════════════════════════════════════════════════

def valid_url(url):

    return bool(
        re.match(
            r"^https?://",
            url,
            re.IGNORECASE
        )
    )


def is_playlist(url):

    text = url.lower()

    return any(
        x in text
        for x in [
            "list=",
            "/playlist",
            "playlist?",
            "/sets/"
        ]
    )


# ══════════════════════════════════════════════════════════════
# ERROR DETECTOR
# ══════════════════════════════════════════════════════════════

def detect_error(error_text):

    text = error_text.lower()

    # Extractor / website changed
    extractor_errors = [

        "unable to extract",

        "please report this issue",

        "universal data for rehydration",

        "unable to download api page",

        "signature extraction failed",

        "nsig extraction failed",

        "unsupported url",
    ]

    for error in extractor_errors:

        if error in text:

            return "UPDATE"

    # Login / private
    login_errors = [

        "login required",

        "sign in",

        "private video",

        "private account",

        "not available in your country",
    ]

    for error in login_errors:

        if error in text:

            return "ACCESS"

    # DRM
    if "drm" in text:

        return "DRM"

    # Network
    network_errors = [

        "connection refused",

        "timed out",

        "network is unreachable",

        "temporary failure",

        "http error 429",

        "too many requests",
    ]

    for error in network_errors:

        if error in text:

            return "NETWORK"

    return "UNKNOWN"


# ══════════════════════════════════════════════════════════════
# FORMAT SCANNER
# ══════════════════════════════════════════════════════════════

def scan_formats(url):

    print()
    print(
        f"{CYAN}  🔍 SCANNING FORMATS...{RESET}"
    )

    subprocess.run(
        [
            "yt-dlp",
            "-F",
            "--no-playlist",
            url
        ]
    )


# ══════════════════════════════════════════════════════════════
# QUALITY MENU
# ══════════════════════════════════════════════════════════════

def quality_menu():

    print()
    line()

    print(
        f"{CYAN}{BOLD}"
        "              SELECT QUALITY"
        f"{RESET}"
    )

    line()

    for key, data in QUALITY_MAP.items():

        name = data[0]

        color = GREEN

        if key == "1":
            color = MAGENTA

        elif key in ("10", "11"):
            color = YELLOW

        print(
            f"  {color}[{key:>2}]{RESET} "
            f"{WHITE}{name}{RESET}"
        )

    line()

    print(f"  {BLUE}[S]{RESET} SCAN FORMATS")
    print(f"  {GRAY}[B]{RESET} BACK")

    line()

    choice = input(
        f"{YELLOW}  SELECT › {RESET}"
    ).strip().lower()

    if choice in QUALITY_MAP:
        return choice

    if choice == "s":
        return "scan"

    return None


# ══════════════════════════════════════════════════════════════
# SPEED MENU
# ══════════════════════════════════════════════════════════════

def speed_menu():

    print()

    line()

    print(
        f"{CYAN}{BOLD}"
        "              SPEED MODE"
        f"{RESET}"
    )

    line()

    print(f"  {GREEN}[1]{RESET} BALANCED  → 4 FRAGMENTS")
    print(f"  {YELLOW}[2]{RESET} FAST      → 8 FRAGMENTS")
    print(f"  {RED}[3]{RESET} ULTRA     → 16 FRAGMENTS")

    line()

    choice = input(
        f"{YELLOW}  SPEED › {RESET}"
    ).strip()

    if choice == "1":
        return 4

    if choice == "3":
        return 16

    return 8


# ══════════════════════════════════════════════════════════════
# BUILD COMMAND
# ══════════════════════════════════════════════════════════════

def build_command(url, choice, fragments):

    name, fmt, audio_only = QUALITY_MAP[choice]

    DL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if is_playlist(url):

        template = str(
            DL_DIR /
            "%(playlist_title).100B" /
            "%(playlist_index)03d - %(title).150B.%(ext)s"
        )

    else:

        template = str(
            DL_DIR /
            "%(title).180B.%(ext)s"
        )

    cmd = [

        "yt-dlp",

        "--newline",

        "--progress",

        "--continue",

        "--concurrent-fragments",
        str(fragments),

        "--buffer-size",
        BUFFER_SIZE,

        "--resize-buffer",

        "--retries",
        MAX_RETRIES,

        "--fragment-retries",
        FRAGMENT_RETRIES,

        "--file-access-retries",
        "5",

        "--retry-sleep",
        "fragment:1",

        "--no-overwrites",

        "--windows-filenames",

        "--trim-filenames",
        "180",

        "--download-archive",
        str(ARCHIVE_FILE),

        "--output",
        template,

        "--format",
        fmt,

        "--no-warnings",
    ]

    ffmpeg = find_ffmpeg()

    if ffmpeg:

        cmd += [
            "--ffmpeg-location",
            ffmpeg
        ]

    if audio_only:

        cmd += [

            "--extract-audio",

            "--audio-format",
            "mp3",

            "--audio-quality",
            "0",
        ]

    else:

        if ffmpeg:

            cmd += [

                "--merge-output-format",
                "mp4"
            ]

    if is_playlist(url):

        cmd.append(
            "--yes-playlist"
        )

    else:

        cmd.append(
            "--no-playlist"
        )

    cmd.append(url)

    return cmd, name


# ══════════════════════════════════════════════════════════════
# DOWNLOAD ATTEMPT
# ══════════════════════════════════════════════════════════════

def run_download(url, choice, fragments):

    cmd, quality_name = build_command(
        url,
        choice,
        fragments
    )

    errors = []

    print()
    print(
        f"{CYAN}"
        "  ⚡ STARTING HIGH SPEED DOWNLOAD..."
        f"{RESET}"
    )

    print()

    proc = subprocess.Popen(

        cmd,

        stdout=subprocess.PIPE,

        stderr=subprocess.STDOUT,

        text=True,

        bufsize=1,

        errors="replace"
    )

    for raw_line in proc.stdout:

        text = raw_line.rstrip()

        if not text:
            continue

        if "[download]" in text and "%" in text:

            show_progress(text)

        elif "ERROR:" in text:

            errors.append(text)

            print()
            print(
                f"{RED}"
                f"  ✖ {text}"
                f"{RESET}"
            )

        elif "[Merger]" in text:

            print()
            print(
                f"{MAGENTA}"
                "  ◆ MERGING VIDEO + AUDIO..."
                f"{RESET}"
            )

        elif "[ExtractAudio]" in text:

            print()
            print(
                f"{MAGENTA}"
                "  ♫ EXTRACTING MP3..."
                f"{RESET}"
            )

    proc.wait()

    return proc.returncode, "\n".join(errors)


# ══════════════════════════════════════════════════════════════
# SMART DOWNLOAD
# ══════════════════════════════════════════════════════════════

def smart_download(url, choice, fragments):

    print()

    line()

    print(
        f"{GREEN}{BOLD}"
        "           SMART AUTO-FIX DOWNLOAD"
        f"{RESET}"
    )

    line()

    status(
        "Speed",
        f"{fragments} FRAGMENTS",
        YELLOW
    )

    status(
        "Quality",
        QUALITY_MAP[choice][0],
        CYAN
    )

    line()

    # ── FIRST ATTEMPT ─────────────────────────────────────────

    code, errors = run_download(
        url,
        choice,
        fragments
    )

    if code == 0:

        print()

        line()

        print(
            f"{GREEN}{BOLD}"
            "             ✓ DOWNLOAD COMPLETE"
            f"{RESET}"
        )

        line()

        return True


    # ── SMART ERROR DETECTION ─────────────────────────────────

    error_type = detect_error(errors)

    print()

    print(
        f"{YELLOW}"
        f"  ⚠ SMART DETECTOR: {error_type}"
        f"{RESET}"
    )


    # ── AUTO UPDATE ───────────────────────────────────────────

    if error_type == "UPDATE":

        print()

        print(
            f"{CYAN}{BOLD}"
            "  ⚡ EXTRACTOR ERROR DETECTED"
            f"{RESET}"
        )

        print(
            f"{CYAN}"
            "  Attempting automatic yt-dlp update..."
            f"{RESET}"
        )

        updated = update_ytdlp()

        if updated:

            print()

            print(
                f"{MAGENTA}{BOLD}"
                "  ⚡ RETRYING DOWNLOAD..."
                f"{RESET}"
            )

            code, errors = run_download(
                url,
                choice,
                fragments
            )

            if code == 0:

                print()

                line()

                print(
                    f"{GREEN}{BOLD}"
                    "          ✓ AUTO-FIX SUCCESSFUL"
                    f"{RESET}"
                )

                line()

                return True


    # ── NETWORK RETRY ─────────────────────────────────────────

    elif error_type == "NETWORK":

        print()

        print(
            f"{YELLOW}"
            "  ⚠ NETWORK ERROR DETECTED"
            f"{RESET}"
        )

        print(
            f"{CYAN}"
            "  Retrying download once..."
            f"{RESET}"
        )

        code, errors = run_download(
            url,
            choice,
            fragments
        )

        if code == 0:

            print()

            print(
                f"{GREEN}"
                "  ✓ RETRY SUCCESSFUL"
                f"{RESET}"
            )

            return True


    # ── ACCESS ERROR ──────────────────────────────────────────

    elif error_type == "ACCESS":

        print()

        print(
            f"{YELLOW}"
            "  ⚠ ACCESS OR LOGIN RESTRICTION"
            f"{RESET}"
        )

        print(
            f"{GRAY}"
            "  Check that you have permission to access this content."
            f"{RESET}"
        )


    # ── DRM ───────────────────────────────────────────────────

    elif error_type == "DRM":

        print()

        print(
            f"{RED}"
            "  ✖ DRM PROTECTED CONTENT"
            f"{RESET}"
        )


    # ── FINAL RESULT ──────────────────────────────────────────

    print()

    line()

    print(
        f"{RED}{BOLD}"
        "            ✖ SMART AUTO-FIX FAILED"
        f"{RESET}"
    )

    print(
        f"{YELLOW}"
        "  Try updating yt-dlp again later or use Format Scan."
        f"{RESET}"
    )

    line()

    return False


# ══════════════════════════════════════════════════════════════
# MAIN MENU
# ══════════════════════════════════════════════════════════════

def main_menu():

    line()

    print(
        f"{MAGENTA}{BOLD}"
        "  [1] DOWNLOAD VIDEO / AUDIO"
        f"{RESET}"
    )

    print(
        f"{CYAN}"
        "  [2] UPDATE yt-dlp"
        f"{RESET}"
    )

    print(
        f"{BLUE}"
        "  [3] SHOW VERSION"
        f"{RESET}"
    )

    print(
        f"{RED}"
        "  [Q] EXIT"
        f"{RESET}"
    )

    line()

    return input(
        f"{CYAN}{BOLD}"
        "  FARAZO › "
        f"{RESET}"
    ).strip().lower()


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():

    try:

        DL_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    except Exception as e:

        print(f"Folder error: {e}")

        sys.exit(1)


    while True:

        clear()

        logo()

        line()

        print(
            f"{MAGENTA}{BOLD}"
            "       ⚡ FARAZO v5.2 SMART AUTO-FIX ⚡"
            f"{RESET}"
        )

        line()


        version = ensure_ytdlp()

        if not version:

            print(
                f"{RED}"
                "  ✖ yt-dlp NOT FOUND"
                f"{RESET}"
            )

            sys.exit(1)


        status(
            "yt-dlp",
            version,
            GREEN
        )


        ffmpeg = find_ffmpeg()

        status(
            "FFmpeg",
            "READY" if ffmpeg else "NOT FOUND",
            GREEN if ffmpeg else RED
        )


        status(
            "Output",
            str(DL_DIR),
            CYAN
        )


        choice = main_menu()


        if choice == "q":

            print()

            print(
                f"{RED}{BOLD}"
                "  FARAZO SESSION CLOSED"
                f"{RESET}"
            )

            break


        if choice == "2":

            update_ytdlp()

            input(
                f"\n{YELLOW}Press ENTER...{RESET}"
            )

            continue


        if choice == "3":

            print()

            print(
                f"{GREEN}"
                f"  yt-dlp VERSION: {get_ytdlp_version()}"
                f"{RESET}"
            )

            input(
                f"\n{YELLOW}Press ENTER...{RESET}"
            )

            continue


        if choice != "1":

            continue


        print()

        url = input(
            f"{CYAN}{BOLD}"
            "  PASTE URL › "
            f"{RESET}"
        ).strip()


        if not valid_url(url):

            print(
                f"{RED}"
                "  ✖ INVALID URL"
                f"{RESET}"
            )

            input(
                f"{YELLOW}Press ENTER...{RESET}"
            )

            continue


        while True:

            quality = quality_menu()

            if quality is None:
                break


            if quality == "scan":

                scan_formats(url)

                input(
                    f"\n{YELLOW}Press ENTER...{RESET}"
                )

                continue


            fragments = speed_menu()


            smart_download(
                url,
                quality,
                fragments
            )

            break


        print()

        print(
            f"{GREEN}"
            "  ✓ FARAZO IS READY FOR THE NEXT URL"
            f"{RESET}"
        )

        input(
            f"{GRAY}"
            "  Press ENTER..."
            f"{RESET}"
        )


if __name__ == "__main__":
    main()
