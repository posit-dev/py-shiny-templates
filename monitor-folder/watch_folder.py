import sys
from datetime import datetime
from pathlib import Path

from watchfiles import run_process

if len(sys.argv) != 3:
    raise ValueError("Expected 2 arguments: watch_folder and last_change")

watch_folder = Path(sys.argv[1])
last_change = Path(sys.argv[2])

if not watch_folder.is_dir():
    raise ValueError(f"watch_folder '{watch_folder}' is not a directory")


# When changes happen, write the current time to a file
def callback(changes):
    with open(last_change, "w") as f:
        f.write(str(datetime.now()))


def target():
    pass


if __name__ == "__main__":
    run_process(watch_folder, callback=callback, target=target)
