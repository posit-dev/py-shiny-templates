# Folder monitoring

<a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny-templates&sourceRef=main&sourceRefType=branch&primaryFile=monitor-folder%2Fapp-express.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' align="right" /></a>

This implements an app which watches a folder to allow users to view and download log files.
The application polls `watch_folder` every second and refreshes when a new file is added to the folder.
This is a useful pattern when your application consumes files which are provided by some other system like an Airflow pipeline.
You can add new files to the folder either by copying and pasting an existing file, or by clicking the "add log file" button.
