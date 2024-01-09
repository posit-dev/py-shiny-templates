# Instructions

Run the app with `shiny run app.py`. In a separate process run `python populate-logs.py`. 
The shiny process will poll the file once a second and if if the file has changed it will refresh any component which depends on the file either directly or indirectly.