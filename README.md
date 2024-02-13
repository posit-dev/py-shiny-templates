# About

This repository hosts Shiny for Python template files which can be initiated with `shiny create`.

# Requirments

Each template should be in its own folder. If there is only a core template the top-level app file should be `app-core.py`.
If the template supports both express and classic, they should be called `app-core.py` and `app-express.py`.
All other files in the directory should work regardless of which top level app file is chosen. Each template should include a `requirements.txt` file.

# Deployment

Apps are automatically deployed to shinyapps.io.
This should just work for applications that have been previously deployed, but you need to follow a few steps to
deploy a new application.
Each deployment retries three times to avoid spurious failures, and caches the result so as not to redeploy applications which have not changed since the last successful deployment.

# Adding a new application

1. Create a new folder for the application, the folder should contain at least an `app-core.py` file and a `requirements.txt` file. Optionally add an `app-expres.py` file if you want to give people the option to use Shiny Express.

2. Deploy the app to shinyapps.io in the `gallery` account, if you don't have access to this account mention it in the PR and a member of the Shiny team will do this and the following step for you.

3. Add your application to `deployments.json`, you will need to login to shinyapps.io to get the guid.

4. Raise a PR with your changes

# Updating Shiny

We want all of the apps to redeploy whenever there is a new Shiny release to make sure that they all reflect the current state of the Shiny package.
To accomplish this we have included the `requirements.txt` file in the deployment cache key.
To update all of the applications to the latest version of Shiny, you can raise a PR which updates the `requirements.txt` file in this repository.
