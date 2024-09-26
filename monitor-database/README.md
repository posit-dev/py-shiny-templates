# Database monitoring

[![](https://docs.posit.co/connect-cloud/images/cc-deploy.svg)](https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny-templates&sourceRef=main&sourceRefType=branch&primaryFile=monitor-database%2Fapp-core.py&pythonVersion=3.11)


Shiny allows you to reactively update your app whenever an external data source changes.
This application simulates that situation by writing data to a sqlite database after a random time period.
Shiny polls the database every second to see if there is any new data, and if there it pulls the updated data and refreshes any elements which depend on that data.

This application also uses dynamic UI to generate informative value boxes which tell the user when the model score falls below a certain threshold.
