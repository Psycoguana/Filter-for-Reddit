import pathlib
import sys
import os

# This sets the Current Working Directory to wherever the script is located.
# Ensuring the script gets the correct path of praw.ini no matter from where it's called.
# To do it, it's important to check if we're running from an exe or not.

if getattr(sys, 'frozen', False):  # Running from an exe
    script_dir = pathlib.Path(
        sys.executable).parent.absolute().parent.absolute()
elif __file__:
    script_dir = pathlib.Path(__file__).parent.absolute()

os.chdir(script_dir)
