import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
from shiny import reactive
from shiny.session import session_context

app_dir = Path(__file__).parent

# The directory to watch for changes
watch_folder = app_dir / "watch_folder"
# The file to update when a change is detected (DO NOT PUT THIS INSIDE `watch_folder`!)
last_change = app_dir / "last_change.txt"

# Start a background process to watch the `watch_folder` directory
# and update the `last_change` file when a change is detected
process = subprocess.Popen(
    ["python", app_dir / "watch_folder.py", str(watch_folder), str(last_change)]
)


# Get filenames and last edited times within the `watch_folder`
# (when a change is detected)
#
# NOTE: the session_context(None) here is only necessary at the moment
# for Express -- this should improve/change in a future release
# https://github.com/posit-dev/py-shiny/issues/1079
with session_context(None):

    @reactive.file_reader(last_change)
    def files_df():
        files_info = []
        for file in watch_folder.glob("*"):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            info = (file.name, mtime.strftime("%Y-%m-%d %H:%M:%S"))
            files_info.append(info)
        return pd.DataFrame(files_info, columns=["File Name", "Last Edited"])
