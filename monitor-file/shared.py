import subprocess
from pathlib import Path

import pandas as pd
from shiny import reactive
from shiny.session import session_context

app_dir = Path(__file__).parent

# Launch process to generate logs
process = subprocess.Popen(["python", app_dir / "populate-logs.py"])


# File reader polls the file (every second by default) for changes
#
# NOTE: the session_context(None) here is only necessary at the moment
# for Express -- this should improve/change in a future release
# https://github.com/posit-dev/py-shiny/issues/1079
with session_context(None):

    @reactive.file_reader(app_dir / "logs.csv")
    def logs_df():
        return pd.read_csv(app_dir / "logs.csv")
