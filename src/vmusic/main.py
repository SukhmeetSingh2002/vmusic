import os
import sys
import argparse
from vmusic.trim import trim_audio
from vmusic.music import run_visualizer
from vmusic import __version__


def main():
    # Check if we can run commands with sudo
    if os.system("sudo -v") != 0:
        print("You need sudo privileges to run this script.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Audio Visualizer")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--file", type=str, help="The audio file to visualize", required=True
    )
    parser.add_argument(
        "--trim", action="store_true", help="Trim the audio file before visualizing"
    )
    parser.add_argument(
        "--start", type=int, default=0, help="The start second for trimming"
    )
    parser.add_argument(
        "--end", type=int, default=30, help="The end second for trimming"
    )
    parser.add_argument(
        "-c", "--change-screen", action="store_true", help="Change the screen brightness"
    )

    args = parser.parse_args()

    if args.trim:
        filename = trim_audio(args.file, args.start, args.end)
    else:
        filename = args.file

    run_visualizer(filename)


if __name__ == "__main__":
    main()
