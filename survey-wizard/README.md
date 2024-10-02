# Multi-page wizard

<a href='https://connect.posit.cloud/publish?framework=shiny&sourceRepositoryURL=https%3A%2F%2Fgithub.com%2Fposit-dev%2Fpy-shiny-templates&sourceRef=main&sourceRefType=branch&primaryFile=survey-wizard%2Fapp-core.py&pythonVersion=3.11'><img src='https://cdn.connect.posit.cloud/assets/deploy-to-connect-blue.svg' align="right" /></a>


This application shows how you would build a multi-page wizard app in Shiny.
This is useful for large apps which have a natural progression from page-to-page.
It illustrates a few Shiny techniques:

1. The application pages are [modules](https://shiny.posit.co/py/docs/workflow-modules.html) which lets you break them apart and work on them separately. The responses for each page are gathered into a reactive calculation which is returned from the server function to the main application.

2. The app uses buttons to navigate through the tabs. Tabsets can serve as inputs to reactive functions, and can also be modified from the server.

3. Modals are used to alert the user to important things, like when they've successfully finished the app.
