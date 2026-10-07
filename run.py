import os
import time
import subprocess

MAIN_FILE = "main.py"

last_modified = os.path.getmtime(MAIN_FILE)

# Start main.py
process = subprocess.Popen(["py", "-3.13", MAIN_FILE])

while True:
    time.sleep(1)

    current_modified = os.path.getmtime(MAIN_FILE)

    if current_modified != last_modified:
        print("Changes detected. Restarting...")

        # Close old program
        process.terminate()
        process.wait()

        # Start new program
        process = subprocess.Popen(["py", "-3.13", MAIN_FILE])

        last_modified = current_modified